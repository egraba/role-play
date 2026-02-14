# Wire Attack Views to Service Module — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Wire `game/views/attack.py` to use the existing `game/attack.py` service module, replacing inline combat math with proper weapon-aware attack resolution.

**Architecture:** The views currently reimplement D&D combat logic inline (hardcoded STR, hardcoded 1d8). The service module `game/attack.py` already has `resolve_attack()` and `apply_damage()` with full SRD 5.2.1 support. We wire views to the service, add weapon selection to the UI, deduplicate the permission check, and update templates.

**Tech Stack:** Django 6.0, HTMX, pytest, factory_boy

---

## Task 1: Enhance AttackResult for UI display data

The template needs individual damage die values (for dice animation) and the discarded d20 roll (for advantage/disadvantage display). `AttackResult` doesn't currently provide these.

**Files:**
- Modify: `game/attack.py:24-51` (AttackResult dataclass)
- Modify: `game/attack.py:106-214` (resolve_attack function)
- Test: `game/tests/test_attack.py`

**Step 1: Write failing tests for new AttackResult fields**

Add to `game/tests/test_attack.py` in `TestResolveAttack`:

```python
def test_attack_result_includes_damage_rolls(self, attacker, target, weapon):
    """Test that AttackResult includes individual damage die values."""
    with patch("game.attack.DiceString.roll_keeping_individual") as mock_roll:
        mock_roll.return_value = (6, [6])
        with patch("game.attack.roll_d20_test") as mock_d20:
            mock_d20.return_value = (25, False, False)  # hit
            result = resolve_attack(attacker, target, weapon)
    assert isinstance(result.damage_rolls, list)
    assert len(result.damage_rolls) > 0


def test_attack_miss_has_empty_damage_rolls(self, attacker, target, weapon):
    """Test that a miss has empty damage_rolls."""
    with patch("game.attack.roll_d20_test") as mock_roll:
        mock_roll.return_value = (2, False, True)  # nat 1
        result = resolve_attack(attacker, target, weapon)
    assert result.damage_rolls == []


def test_advantage_includes_second_natural_roll(self, attacker, target, weapon):
    """Test that advantage attack includes the discarded roll."""
    with patch("game.attack.roll_d20_test") as mock_roll:
        mock_roll.return_value = (25, False, False)
        with patch("game.attack.DiceString.roll_keeping_individual") as mock_dmg:
            mock_dmg.return_value = (6, [6])
            result = resolve_attack(
                attacker, target, weapon, advantage=True
            )
    # second_natural_roll is populated when advantage/disadvantage used
    # (exact value depends on mock, but field should exist)
    assert hasattr(result, "second_natural_roll")
```

**Step 2: Run tests to verify they fail**

Run: `doppler run -- uv run pytest game/tests/test_attack.py::TestResolveAttack::test_attack_result_includes_damage_rolls -v`
Expected: FAIL — `AttackResult` has no `damage_rolls` field

**Step 3: Add fields to AttackResult**

In `game/attack.py`, add two fields to `AttackResult`:

```python
# Add after mastery_effect field (line ~51)
damage_rolls: list[int] = field(default_factory=list)
second_natural_roll: int | None = None
```

**Step 4: Populate damage_rolls in resolve_attack**

In `resolve_attack`, replace the damage rolling block (lines ~170-178):

```python
# OLD:
if is_hit:
    dice = DiceString(damage_dice)
    damage = dice.roll_damage(critical=is_critical_hit) + damage_modifier
    damage = max(0, damage)

# NEW:
damage_rolls = []
if is_hit:
    dice = DiceString(damage_dice)
    _, damage_rolls = dice.roll_keeping_individual()
    if is_critical_hit:
        _, crit_rolls = dice.roll_keeping_individual()
        damage_rolls = damage_rolls + crit_rolls
    damage = sum(damage_rolls) + damage_modifier
    damage = max(0, damage)
```

And add `damage_rolls=damage_rolls` to the `AttackResult(...)` constructor at the end.

**Step 5: Populate second_natural_roll in resolve_attack**

Replace the d20 rolling section to capture both rolls. Instead of using `roll_d20_test`, inline the logic using `DiceString`:

```python
# OLD:
attack_roll, is_nat_20, is_nat_1 = roll_d20_test(
    modifier=attack_modifier,
    advantage=advantage,
    disadvantage=disadvantage,
)
natural_roll = attack_roll - attack_modifier

# NEW:
d20 = DiceString("d20")
second_natural_roll = None

if advantage and disadvantage:
    _, rolls = d20.roll_keeping_individual()
    natural_roll = rolls[0]
elif advantage:
    _, roll1, roll2 = d20.roll_with_advantage()
    natural_roll = max(roll1, roll2)
    second_natural_roll = min(roll1, roll2)
elif disadvantage:
    _, roll1, roll2 = d20.roll_with_disadvantage()
    natural_roll = min(roll1, roll2)
    second_natural_roll = max(roll1, roll2)
else:
    _, rolls = d20.roll_keeping_individual()
    natural_roll = rolls[0]

attack_roll = natural_roll + attack_modifier
is_nat_20 = natural_roll == 20
is_nat_1 = natural_roll == 1
```

And add `second_natural_roll=second_natural_roll` to the `AttackResult(...)` constructor.

Remove the now-unused `roll_d20_test` import if no longer needed in this file.

**Step 6: Run all attack tests**

Run: `doppler run -- uv run pytest game/tests/test_attack.py game/tests/test_mastery.py -v`
Expected: Some existing tests may need mock path updates (from `game.attack.roll_d20_test` to `game.attack.DiceString`). Fix any failures.

**Step 7: Commit**

```bash
git add game/attack.py game/tests/test_attack.py
git commit -m "feat: enhance AttackResult with damage_rolls and second_natural_roll for UI"
```

---

## Task 2: Extract CombatTurnPermissionMixin

The `test_func()` method is copy-pasted across `AttackModalView`, `AttackRollView`, `DamageRollView`, and `ApplyDamageView`.

**Files:**
- Modify: `game/views/attack.py:59-71, 88-100, 176-188, 260-272` (4 identical test_func methods)
- Test: `game/tests/views/test_attack_modal.py` (existing tests cover permission behavior)

**Step 1: Run existing permission tests to establish baseline**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py::TestAttackModalView::test_modal_forbidden_when_not_your_turn game/tests/views/test_attack_modal.py::TestApplyDamageView::test_apply_damage_forbidden_when_not_your_turn -v`
Expected: PASS

**Step 2: Create CombatTurnPermissionMixin in game/views/attack.py**

Add before `AttackModalMixin` (around line 20):

```python
class CombatTurnPermissionMixin(UserPassesTestMixin):
    """Mixin that verifies the requesting user is the current fighter in active combat."""

    def test_func(self) -> bool:
        combat_id = self.kwargs.get("combat_id")
        try:
            combat = Combat.objects.get(id=combat_id, game=self.game)
            if combat.state != CombatState.ACTIVE:
                return False
            current_fighter = combat.current_fighter
            if not current_fighter:
                return False
            return current_fighter.player.user == self.request.user
        except Combat.DoesNotExist:
            return False
```

**Step 3: Replace test_func in all 4 view classes**

Replace `UserPassesTestMixin` with `CombatTurnPermissionMixin` in:
- `AttackModalView` — remove `UserPassesTestMixin` and its `test_func`
- `AttackRollView` — remove `UserPassesTestMixin` and its `test_func`
- `DamageRollView` — remove `UserPassesTestMixin` and its `test_func`
- `ApplyDamageView` — remove `UserPassesTestMixin` and its `test_func`

Example: `class AttackModalView(CombatTurnPermissionMixin, AttackModalMixin, GameContextMixin, View):`

**Step 4: Run all attack view tests**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py -v`
Expected: All PASS — behavior is identical.

**Step 5: Commit**

```bash
git add game/views/attack.py
git commit -m "refactor: extract CombatTurnPermissionMixin from 4 duplicated test_func methods"
```

---

## Task 3: Wire AttackModalMixin to include weapons

Add weapon list to the attack modal context so Phase 1 shows a weapon selector.

**Files:**
- Modify: `game/views/attack.py:20-53` (AttackModalMixin)
- Test: `game/tests/views/test_attack_modal.py`

**Step 1: Write failing test for weapon list in modal**

Add to `TestAttackModalView` in `game/tests/views/test_attack_modal.py`:

```python
def test_modal_shows_weapon_selector(self, client, active_combat_setup):
    """Test modal displays weapon selection dropdown."""
    setup = active_combat_setup
    client.force_login(setup["player1"].user)

    url = reverse(
        "combat-attack-modal",
        args=(setup["game"].id, setup["combat"].id),
    )
    response = client.get(url)

    content = response.content.decode()
    assert "Select Weapon" in content
```

Update `active_combat_setup` fixture to add a weapon to character1's inventory:

```python
from equipment.constants.equipment import WeaponName, WeaponType
from equipment.models.equipment import Weapon, WeaponSettings

# After creating character1, add a weapon:
weapon_settings, _ = WeaponSettings.objects.update_or_create(
    name=WeaponName.LONGSWORD,
    defaults={
        "weapon_type": WeaponType.MARTIAL_MELEE,
        "cost": 15,
        "damage": "1d8",
        "weight": 3,
        "properties": "versatile",
    },
)
weapon = Weapon.objects.create(
    settings=weapon_settings,
    inventory=character1.inventory,
)
```

Add `"weapon": weapon` to the returned dict.

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py::TestAttackModalView::test_modal_shows_weapon_selector -v`
Expected: FAIL — "Select Weapon" not in content

**Step 3: Update AttackModalMixin.get_attack_context**

In `game/views/attack.py`, add weapon imports and modify `get_attack_context`:

```python
from equipment.models.equipment import Weapon
from ..attack import get_attack_ability

# In get_attack_context, replace the hardcoded attack bonus calculation:
def get_attack_context(self, combat, user, fighter):
    targets = Fighter.objects.filter(combat=combat).exclude(id=fighter.id)
    character = fighter.character

    # Get weapons from character's inventory
    weapons = Weapon.objects.filter(
        inventory=character.inventory
    ).select_related("settings")

    # Calculate attack bonus per weapon for display
    weapon_data = []
    for weapon in weapons:
        ability_name = get_attack_ability(weapon, character)
        ability = character.abilities.filter(
            ability_type__name=ability_name
        ).first()
        ability_modifier = ability.modifier if ability else 0
        proficiency = getattr(character, "proficiency_bonus", 2)
        attack_bonus = ability_modifier + proficiency
        weapon_data.append({
            "weapon": weapon,
            "attack_bonus": attack_bonus,
            "ability": ability_name,
            "damage": weapon.settings.damage or "1d4",
        })

    return {
        "combat": combat,
        "fighter": fighter,
        "targets": targets,
        "weapons": weapon_data,
        "attack_bonus": weapon_data[0]["attack_bonus"] if weapon_data else 0,
        "show_modal": True,
    }
```

**Step 4: Update template Phase 1 to show weapon selector**

In `game/templates/game/partials/attack_modal.html`, add a weapon `<select>` after the target selector in Phase 1:

```html
<!-- Weapon Selection (add after target selection div) -->
<div class="attack-section">
    <label class="attack-label">
        <img src="{% static 'images/icons/actions/attack.svg' %}" alt="" class="rpg-icon rpg-icon-sm">
        Select Weapon
    </label>
    <select name="weapon_id" class="rpg-select weapon-select" required>
        {% for wd in weapons %}
            <option value="{{ wd.weapon.id }}"
                    data-attack-bonus="{{ wd.attack_bonus }}"
                    data-damage="{{ wd.damage }}">
                {{ wd.weapon.settings.name }} ({{ wd.damage }}, +{{ wd.attack_bonus }})
            </option>
        {% empty %}
            <option value="">-- No weapons equipped --</option>
        {% endfor %}
    </select>
</div>
```

**Step 5: Run tests**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py::TestAttackModalView -v`
Expected: All PASS

**Step 6: Commit**

```bash
git add game/views/attack.py game/templates/game/partials/attack_modal.html game/tests/views/test_attack_modal.py
git commit -m "feat: add weapon selection to attack modal with per-weapon attack bonus"
```

---

## Task 4: Wire AttackRollView to use resolve_attack

Replace inline d20/hit-miss logic with a single `resolve_attack()` call.

**Files:**
- Modify: `game/views/attack.py:85-170` (AttackRollView)
- Test: `game/tests/views/test_attack_modal.py`

**Step 1: Update existing test fixtures to include weapon**

Ensure `TestAttackRollView.active_combat_setup` also creates a weapon (same pattern as Task 3). Update all POST data in `TestAttackRollView` tests to include `"weapon_id": setup["weapon"].id`.

**Step 2: Update mock paths in tests**

The tests currently mock `game.views.attack.random.randint`. After this change, the views call `resolve_attack` which uses `DiceString` internally. Update mocks to patch `game.attack.DiceString` methods or `game.views.attack.resolve_attack` directly.

For tests that check specific roll values (critical hit, advantage), mock `resolve_attack` itself:

```python
from game.attack import AttackResult

@patch("game.views.attack.resolve_attack")
def test_attack_roll_shows_critical_hit(self, mock_resolve, client, active_combat_setup):
    """Test natural 20 shows critical hit."""
    setup = active_combat_setup
    mock_resolve.return_value = AttackResult(
        attack_roll=25,
        natural_roll=20,
        attack_modifier=5,
        target_ac=15,
        is_hit=True,
        is_critical_hit=True,
        is_critical_miss=False,
        damage=12,
        damage_dice="1d8",
        damage_modifier=3,
        attacker_name="Attacker",
        target_name="Target",
        weapon_name="Longsword",
        ability_used="Strength",
        damage_rolls=[8],
    )
    client.force_login(setup["player1"].user)
    url = reverse("combat-attack-roll", args=(setup["game"].id, setup["combat"].id))
    response = client.post(url, {
        "target_id": setup["fighter2"].id,
        "weapon_id": setup["weapon"].id,
        "roll_modifier": "normal",
    })
    content = response.content.decode()
    assert "CRITICAL HIT" in content
```

Apply same pattern for critical miss, advantage, and disadvantage tests.

**Step 3: Run tests to verify they fail**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py::TestAttackRollView -v`
Expected: FAIL — views don't accept weapon_id yet

**Step 4: Rewrite AttackRollView.post()**

```python
def post(self, request, *args, **kwargs):
    """Process the attack roll and return results."""
    combat_id = kwargs.get("combat_id")
    combat = Combat.objects.get(id=combat_id, game=self.game)
    fighter = combat.current_fighter

    target_id = request.POST.get("target_id")
    weapon_id = request.POST.get("weapon_id")
    roll_modifier = request.POST.get("roll_modifier", "normal")

    # Validate target
    try:
        target = Fighter.objects.get(id=target_id, combat=combat)
    except Fighter.DoesNotExist:
        context = self.get_attack_context(combat, request.user, fighter)
        context["error"] = "Invalid target selected"
        return HttpResponse(self.render_attack_modal(context, self.game))

    # Validate weapon
    try:
        weapon = Weapon.objects.get(id=weapon_id, inventory=fighter.character.inventory)
    except Weapon.DoesNotExist:
        context = self.get_attack_context(combat, request.user, fighter)
        context["error"] = "Invalid weapon selected"
        return HttpResponse(self.render_attack_modal(context, self.game))

    # Resolve the attack using the service module
    result = resolve_attack(
        attacker=fighter.character,
        target=target.character,
        weapon=weapon,
        advantage=(roll_modifier == "advantage"),
        disadvantage=(roll_modifier == "disadvantage"),
    )

    # Build result context
    context = self.get_attack_context(combat, request.user, fighter)
    context.update({
        "attack_result": True,
        "target": target,
        "natural_roll": result.natural_roll,
        "second_roll": result.second_natural_roll,
        "roll_modifier": roll_modifier,
        "attack_bonus": result.attack_modifier,
        "total_roll": result.attack_roll,
        "is_hit": result.is_hit,
        "is_critical_hit": result.is_critical_hit,
        "is_critical_miss": result.is_critical_miss,
        "weapon_name": result.weapon_name,
        "weapon_id": weapon.id,
        # Pre-computed damage (displayed in Phase 2b)
        "damage_rolls": result.damage_rolls,
        "damage_formula": self._build_damage_formula(result),
        "total_damage": result.damage,
        "animate": True,
    })

    html = self.render_attack_modal(context, self.game)
    return HttpResponse(html)
```

Add a helper to the mixin or view for building the damage formula string:

```python
@staticmethod
def _build_damage_formula(result):
    """Build a human-readable damage formula from AttackResult."""
    if not result.damage_rolls:
        return ""
    rolls_str = "+".join(map(str, result.damage_rolls))
    dice_count = len(result.damage_rolls)
    return f"{dice_count}d? ({rolls_str}) + {result.damage_modifier}"
```

Add these imports to the top of `game/views/attack.py`:

```python
from ..attack import resolve_attack, apply_damage
from equipment.models.equipment import Weapon
```

Remove `import random` (no longer needed).

**Step 5: Run tests**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py::TestAttackRollView -v`
Expected: All PASS

**Step 6: Commit**

```bash
git add game/views/attack.py game/tests/views/test_attack_modal.py
git commit -m "refactor: wire AttackRollView to resolve_attack service"
```

---

## Task 5: Wire DamageRollView as display-only pass-through

The damage is already computed in Phase 2. DamageRollView now receives the pre-computed values via hidden fields and displays them.

**Files:**
- Modify: `game/views/attack.py:173-252` (DamageRollView)
- Modify: `game/templates/game/partials/attack_modal.html` (hidden fields in Phase 2)
- Test: `game/tests/views/test_attack_modal.py`

**Step 1: Update template to pass pre-computed damage as hidden fields**

In the "Roll Damage" form (Phase 2 of template), add hidden fields carrying the pre-computed damage:

```html
<!-- Replace the existing Roll Damage form hidden fields -->
<input type="hidden" name="target_id" value="{{ target.id }}">
<input type="hidden" name="weapon_id" value="{{ weapon_id }}">
<input type="hidden" name="is_critical" value="{{ is_critical_hit|yesno:'true,false' }}">
<input type="hidden" name="natural_roll" value="{{ natural_roll }}">
<input type="hidden" name="total_roll" value="{{ total_roll }}">
<input type="hidden" name="total_damage" value="{{ total_damage }}">
<input type="hidden" name="damage_rolls" value="{{ damage_rolls|join:',' }}">
<input type="hidden" name="damage_formula" value="{{ damage_formula }}">
<input type="hidden" name="attack_bonus" value="{{ attack_bonus }}">
```

**Step 2: Update test fixtures and assertions**

Update `TestDamageRollView` tests to POST the new fields (`total_damage`, `damage_rolls`, `damage_formula`, `weapon_id`). Remove mocks of `random.randint` since DamageRollView no longer rolls dice.

**Step 3: Rewrite DamageRollView.post()**

```python
def post(self, request, *args, **kwargs):
    """Display pre-computed damage results."""
    combat_id = kwargs.get("combat_id")
    combat = Combat.objects.get(id=combat_id, game=self.game)
    fighter = combat.current_fighter

    target_id = request.POST.get("target_id")
    is_critical = request.POST.get("is_critical") == "true"
    natural_roll = int(request.POST.get("natural_roll", 0))
    total_roll = int(request.POST.get("total_roll", 0))
    attack_bonus = int(request.POST.get("attack_bonus", 0))
    total_damage = int(request.POST.get("total_damage", 0))
    damage_rolls_str = request.POST.get("damage_rolls", "")
    damage_formula = request.POST.get("damage_formula", "")

    try:
        target = Fighter.objects.get(id=target_id, combat=combat)
    except Fighter.DoesNotExist:
        return HttpResponse("Invalid target", status=400)

    # Parse damage rolls from comma-separated string
    damage_rolls = [int(d) for d in damage_rolls_str.split(",") if d.strip()]

    context = self.get_attack_context(combat, request.user, fighter)
    context.update({
        "attack_result": True,
        "target": target,
        "natural_roll": natural_roll,
        "attack_bonus": attack_bonus,
        "total_roll": total_roll,
        "is_hit": True,
        "is_critical_hit": is_critical,
        "is_critical_miss": False,
        "damage_rolled": True,
        "damage_dice": damage_rolls,
        "damage_formula": damage_formula,
        "total_damage": total_damage,
    })

    html = self.render_attack_modal(context, self.game)
    return HttpResponse(html)
```

**Step 4: Run tests**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py::TestDamageRollView -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add game/views/attack.py game/templates/game/partials/attack_modal.html game/tests/views/test_attack_modal.py
git commit -m "refactor: wire DamageRollView as display-only pass-through"
```

---

## Task 6: Wire ApplyDamageView to use apply_damage

Replace `target_character.take_damage()` with `apply_damage()` from the service.

**Files:**
- Modify: `game/views/attack.py:255-342` (ApplyDamageView)
- Test: `game/tests/views/test_attack_modal.py` (existing tests should still pass)

**Step 1: Run existing tests to establish baseline**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py::TestApplyDamageView -v`
Expected: All PASS

**Step 2: Replace take_damage with apply_damage**

In `ApplyDamageView.post()`, replace:

```python
# OLD:
target_character.take_damage(damage)

# NEW:
apply_damage(target_character, damage)
```

The `apply_damage` import was already added in Task 4.

**Step 3: Run all tests**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py::TestApplyDamageView -v`
Expected: All PASS — `apply_damage` also sets hp to `max(0, hp - damage)` and saves.

**Step 4: Commit**

```bash
git add game/views/attack.py
git commit -m "refactor: wire ApplyDamageView to use apply_damage service function"
```

---

## Task 7: Template polish — weapon name and damage type display

Update the template to show weapon-specific information throughout the attack flow.

**Files:**
- Modify: `game/templates/game/partials/attack_modal.html`
- Test: `game/tests/views/test_attack_modal.py` (add assertion for weapon name display)

**Step 1: Write failing test**

```python
def test_attack_result_shows_weapon_name(self, client, active_combat_setup):
    """Test attack result displays the weapon name."""
    # ... (setup, login, POST with weapon_id)
    content = response.content.decode()
    assert "Longsword" in content
```

**Step 2: Update template to show weapon name**

In the attack result section (Phase 2), add weapon name display in the target info area:

```html
<div class="target-info">
    <span class="target-name">{{ target.character.name }}</span>
    {% if weapon_name %}
        <span class="weapon-name">{{ weapon_name }}</span>
    {% endif %}
    <span class="target-ac">AC {{ target.character.ac|default:"10" }}</span>
</div>
```

Also add `weapon_id` as a hidden field in the "Apply Damage" form for traceability:

```html
<input type="hidden" name="weapon_id" value="{{ weapon_id }}">
```

**Step 3: Run all attack view tests**

Run: `doppler run -- uv run pytest game/tests/views/test_attack_modal.py -v`
Expected: All PASS

**Step 4: Commit**

```bash
git add game/templates/game/partials/attack_modal.html game/tests/views/test_attack_modal.py
git commit -m "feat: display weapon name in attack result modal"
```

---

## Task 8: Clean up unused imports and run full test suite

**Files:**
- Modify: `game/views/attack.py` (remove unused imports)

**Step 1: Remove unused imports**

Remove from `game/views/attack.py`:
- `import random` (no longer used)
- `from django.contrib.auth.mixins import UserPassesTestMixin` (replaced by mixin that imports it)

**Step 2: Run pre-commit**

Run: `pre-commit run --all-files`
Expected: All PASS

**Step 3: Run full test suite**

Run: `doppler run -- uv run poe test`
Expected: All PASS

**Step 4: Commit**

```bash
git add game/views/attack.py
git commit -m "chore: clean up unused imports in attack views"
```

---

## Task 9: Update CHANGELOG.md

**Files:**
- Modify: `CHANGELOG.md`

**Step 1: Add entry under ## Unreleased**

```markdown
### Changed
- Attack views now use `game/attack.py` service module instead of inline combat math
- Attack modal now includes weapon selection with per-weapon attack bonuses
- Attack resolution uses actual weapon damage dice instead of hardcoded 1d8
- Attack ability selection follows SRD 5.2.1 (STR/DEX/finesse) based on weapon
- Extracted `CombatTurnPermissionMixin` from 4 duplicated permission checks
```

**Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: update changelog for attack view service wiring"
```
