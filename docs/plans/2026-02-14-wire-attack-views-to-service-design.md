# Wire Attack Views to Service Module

**Date**: 2026-02-14
**Branch**: `refactor/attack-views-service`
**Scope**: `game/views/attack.py`, `game/attack.py`, attack modal template

## Problem

The attack flow in `game/views/attack.py` reimplements D&D 5e combat math inline across 4 view classes (343 lines), while `game/attack.py` already provides a complete, tested service module (`resolve_attack()`, `apply_damage()`, `AttackResult` dataclass) that no view uses.

Current issues:
- Attack bonus hardcodes STR modifier (ignores DEX, finesse, ranged weapons)
- Damage hardcodes `1d8` (ignores actual weapon damage dice)
- Uses `random.randint` instead of `roll_d20_test` utility
- No weapon selection — players can't choose which weapon to attack with
- No weapon mastery support
- Attack bonus calculation duplicated 3 times across views
- `test_func()` permission check copy-pasted 4 times

## Design

### Phase 1: Target & Weapon Selection (AttackModalView)

`AttackModalMixin.get_attack_context()` adds weapons from the character's inventory:

```python
weapons = Weapon.objects.filter(
    inventory=character.inventory
).select_related("settings")
```

Template gets a weapon `<select>` dropdown. Attack bonus display shows the bonus for the selected weapon (based on STR/DEX/finesse logic via `get_attack_ability()`).

### Phase 2: Unified Attack Roll (AttackRollView)

`AttackRollView.post()` receives `weapon_id`, looks up the `Weapon`, and calls:

```python
result = resolve_attack(
    attacker=character,
    target=target.character,
    weapon=weapon,
    advantage=(roll_modifier == "advantage"),
    disadvantage=(roll_modifier == "disadvantage"),
)
```

`AttackResult` provides all template context: `natural_roll`, `attack_modifier`, `is_hit`, `is_critical_hit`, `damage`, `damage_dice`, `weapon_name`, `ability_used`, `mastery_effect`.

### Phase 2b: Damage Display (DamageRollView)

Kept for UX (separate "Roll Damage" click) but becomes a thin pass-through — displays pre-computed damage from hidden form fields rather than re-rolling. No business logic.

### Phase 3: Apply Damage (ApplyDamageView)

Calls `apply_damage(target, damage)` from `game/attack.py` instead of `target_character.take_damage()` directly. Turn usage, event creation, and concentration check remain unchanged.

### Deduplication

Extract duplicated `test_func()` into a `CombatTurnPermissionMixin`:

```python
class CombatTurnPermissionMixin(UserPassesTestMixin, GameContextMixin):
    def test_func(self):
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

### Template Changes

- Phase 1: Add weapon selector `<select>` with weapon name + damage dice display
- Phase 2: Show weapon name, ability used, and actual damage dice in results
- Phase 2b: Show damage dice matching the weapon (not hardcoded 1d8)
- Hidden fields pass `weapon_id` through all phases

### What Stays the Same

- 3-phase modal UX flow (selection → results → confirmation)
- HTMX interaction pattern
- Concentration check flow (`check_concentration_on_damage`)
- Event broadcasting (`send_to_channel`)
- URL routing

## Test Strategy

- `game/attack.py` already has thorough unit tests — no changes needed
- Update existing view tests to pass `weapon_id` in POST data
- Add integration test: attack with finesse weapon uses DEX when DEX > STR
- No migrations needed (pure view/service wiring)

## Files Modified

- `game/views/attack.py` — wire to service, add mixin, add weapon handling
- `game/templates/game/partials/attack_modal.html` — weapon selector, weapon-aware display
- `game/tests/` — update view tests with weapon_id

## Files Not Modified

- `game/attack.py` — already complete, no changes needed
- `game/models/` — no model changes
- URL routing — no new endpoints
