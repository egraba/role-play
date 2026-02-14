# Normalize Remaining MonsterSettings JSON Fields — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove the 6 remaining JSONFields from MonsterSettings (traits, actions, reactions, legendary_actions, lair_actions, spellcasting) by wiring up existing relational models and creating a new MonsterSpellcasting model, following the same 3-step migration pattern from PR #446.

**Architecture:** Rename JSONFields with `_json` suffix, add `@cached_property` methods that read from relational tables and return the same dict/list interfaces, write a data migration to populate relational tables from JSON, then drop the old columns. Templates and tests require zero changes.

**Tech Stack:** Django 6.0, PostgreSQL, YAML fixtures, pytest

---

## Prerequisites

- Branch: `refactor/normalize-remaining-json`
- Design doc: `docs/plans/2026-02-14-normalize-remaining-json-fields-design.md`
- Reference: PR #446 migrations 0002-0004 for the established pattern

---

### Task 1: Add MonsterSpellcasting models and backward-compat properties

**Files:**
- Modify: `bestiary/models/monsters.py`

**Step 1: Add MonsterSpellcasting and MonsterSpellcastingLevel models**

Add after the `MonsterLanguage` class (end of file) in `bestiary/models/monsters.py`:

```python
class MonsterSpellcasting(models.Model):
    """Spellcasting ability block for a monster."""

    monster = models.OneToOneField(
        MonsterSettings,
        on_delete=models.CASCADE,
        related_name="spellcasting_entry",
    )
    ability = models.CharField(
        max_length=3,
        help_text="Spellcasting ability abbreviation (INT, WIS, CHA)",
    )
    save_dc = models.PositiveSmallIntegerField()
    attack_bonus = models.SmallIntegerField()

    class Meta:
        db_table = "character_monsterspellcasting"
        verbose_name = "monster spellcasting"
        verbose_name_plural = "monster spellcasting"

    def __str__(self):
        return f"{self.monster.name}: {self.ability} (DC {self.save_dc})"


class MonsterSpellcastingLevel(models.Model):
    """Spells known at a specific level for a spellcasting monster."""

    spellcasting = models.ForeignKey(
        MonsterSpellcasting,
        on_delete=models.CASCADE,
        related_name="levels",
    )
    level = models.CharField(
        max_length=10,
        help_text="Spell level: 'cantrips', '1st', '2nd', ... '9th'",
    )
    slots = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of spell slots (0 for cantrips)",
    )
    spells = models.JSONField(
        default=list,
        help_text="List of spell name strings",
    )

    class Meta:
        db_table = "character_monsterspellcastinglevel"
        constraints = [
            models.UniqueConstraint(
                fields=["spellcasting", "level"],
                name="unique_monster_spellcasting_level",
            ),
        ]
        ordering = ["spellcasting", "level"]
        verbose_name = "monster spellcasting level"
        verbose_name_plural = "monster spellcasting levels"

    def __str__(self):
        return f"{self.spellcasting.monster.name}: {self.level} ({len(self.spells)} spells)"
```

**Step 2: Rename the 6 JSONFields on MonsterSettings with `_json` suffix**

In the `MonsterSettings` class definition, rename:
- `traits` → `traits_json`
- `actions` → `actions_json`
- `reactions` → `reactions_json`
- `legendary_actions` → `legendary_actions_json`
- `lair_actions` → `lair_actions_json`
- `spellcasting` → `spellcasting_json`

**Step 3: Add `@cached_property` backward-compatible methods**

Add these to the `MonsterSettings` class, in the existing backward-compat section (after the `languages` property, around line 270):

```python
@cached_property
def traits(self) -> list[dict]:
    return list(
        self.trait_templates.values("name", "description").order_by(
            "sort_order", "name"
        )
    )

@cached_property
def actions(self) -> list[dict]:
    return list(
        self.action_templates.values(
            "name", "description", "attack_bonus", "damage_dice"
        ).order_by("sort_order", "name")
    )

@cached_property
def reactions(self) -> list[dict]:
    return list(
        self.reaction_templates.values("name", "description").order_by("name")
    )

@cached_property
def legendary_actions(self) -> list[dict]:
    return list(
        self.legendary_action_templates.values(
            "name", "description", "cost"
        ).order_by("sort_order", "cost", "name")
    )

@cached_property
def lair_actions(self) -> list[dict]:
    return list(
        self.lair_action_templates.values("description").order_by("sort_order")
    )

@cached_property
def spellcasting(self) -> dict:
    try:
        entry = self.spellcasting_entry
    except MonsterSpellcasting.DoesNotExist:
        return {}
    result: dict = {
        "ability": entry.ability,
        "save_dc": entry.save_dc,
        "attack_bonus": entry.attack_bonus,
        "spells": {},
    }
    for level in entry.levels.order_by("level"):
        if level.level == "cantrips":
            result["spells"]["cantrips"] = level.spells
        else:
            result["spells"][level.level] = {
                "slots": level.slots,
                "spells": level.spells,
            }
    return result
```

**Step 4: Update the exports**

Add `MonsterSpellcasting` and `MonsterSpellcastingLevel` to any `__all__` or import statements as needed. The test file (`character/tests/models/test_monsters.py`) and factory file (`character/tests/factories.py`) already import from `bestiary.models.monsters` — add the new models to their import blocks.

**Step 5: Run makemigrations**

Run: `doppler run -- uv run python manage.py makemigrations bestiary`

This should generate migration `0005` that:
- Renames the 6 fields with `_json` suffix
- Creates `MonsterSpellcasting` and `MonsterSpellcastingLevel` tables

Verify the generated migration has `RenameField` operations (not `RemoveField` + `AddField`). If Django prompts "Did you rename X to Y?", answer yes for all 6.

**Step 6: Commit**

```bash
git add bestiary/models/monsters.py bestiary/migrations/0005_*.py character/tests/factories.py character/tests/models/test_monsters.py
git commit -m "refactor: rename remaining JSON fields, add spellcasting models and compat properties"
```

---

### Task 2: Write data migration

**Files:**
- Create: `bestiary/migrations/0006_migrate_remaining_json.py`

**Step 1: Create the data migration file**

```python
"""
Step 2 of 3: Migrate data from remaining JSON fields to relational tables.

Copies traits, actions, reactions, legendary_actions, lair_actions,
and spellcasting from the renamed _json fields into their respective
relational models.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    MonsterSettings = apps.get_model("bestiary", "MonsterSettings")
    MonsterTrait = apps.get_model("bestiary", "MonsterTrait")
    MonsterActionTemplate = apps.get_model("bestiary", "MonsterActionTemplate")
    MonsterReaction = apps.get_model("bestiary", "MonsterReaction")
    LegendaryActionTemplate = apps.get_model("bestiary", "LegendaryActionTemplate")
    LairActionTemplate = apps.get_model("bestiary", "LairActionTemplate")
    MonsterSpellcasting = apps.get_model("bestiary", "MonsterSpellcasting")
    MonsterSpellcastingLevel = apps.get_model("bestiary", "MonsterSpellcastingLevel")

    for ms in MonsterSettings.objects.all():
        # Traits
        for i, trait in enumerate(ms.traits_json or []):
            MonsterTrait.objects.create(
                monster=ms,
                name=trait["name"],
                description=trait["description"],
                sort_order=i,
            )

        # Actions
        for i, action in enumerate(ms.actions_json or []):
            MonsterActionTemplate.objects.create(
                monster=ms,
                name=action["name"],
                description=action.get("description", ""),
                attack_bonus=action.get("attack_bonus"),
                damage_dice=action.get("damage_dice", ""),
                sort_order=i,
            )

        # Reactions
        for reaction in ms.reactions_json or []:
            MonsterReaction.objects.create(
                monster=ms,
                name=reaction["name"],
                description=reaction.get("description", ""),
                trigger=reaction.get("trigger", ""),
            )

        # Legendary actions
        for i, la in enumerate(ms.legendary_actions_json or []):
            LegendaryActionTemplate.objects.create(
                monster=ms,
                name=la["name"],
                description=la.get("description", ""),
                cost=la.get("cost", 1),
                sort_order=i,
            )

        # Lair actions
        for i, la in enumerate(ms.lair_actions_json or []):
            LairActionTemplate.objects.create(
                monster=ms,
                description=la.get("description", ""),
                sort_order=i,
            )

        # Spellcasting
        sc_data = ms.spellcasting_json
        if sc_data and sc_data.get("ability"):
            sc = MonsterSpellcasting.objects.create(
                monster=ms,
                ability=sc_data["ability"],
                save_dc=sc_data.get("save_dc", 0),
                attack_bonus=sc_data.get("attack_bonus", 0),
            )
            for level_key, level_data in (sc_data.get("spells") or {}).items():
                if level_key == "cantrips":
                    # Cantrips are stored as a flat list
                    MonsterSpellcastingLevel.objects.create(
                        spellcasting=sc,
                        level="cantrips",
                        slots=0,
                        spells=level_data if isinstance(level_data, list) else [],
                    )
                else:
                    # Leveled spells: {"slots": N, "spells": [...]}
                    if isinstance(level_data, dict):
                        MonsterSpellcastingLevel.objects.create(
                            spellcasting=sc,
                            level=level_key,
                            slots=level_data.get("slots", 0),
                            spells=level_data.get("spells", []),
                        )


def backwards(apps, schema_editor):
    """Reverse: copy relational data back into JSON fields."""
    MonsterSettings = apps.get_model("bestiary", "MonsterSettings")
    MonsterTrait = apps.get_model("bestiary", "MonsterTrait")
    MonsterActionTemplate = apps.get_model("bestiary", "MonsterActionTemplate")
    MonsterReaction = apps.get_model("bestiary", "MonsterReaction")
    LegendaryActionTemplate = apps.get_model("bestiary", "LegendaryActionTemplate")
    LairActionTemplate = apps.get_model("bestiary", "LairActionTemplate")
    MonsterSpellcasting = apps.get_model("bestiary", "MonsterSpellcasting")

    for ms in MonsterSettings.objects.all():
        ms.traits_json = [
            {"name": t.name, "description": t.description}
            for t in MonsterTrait.objects.filter(monster=ms).order_by("sort_order", "name")
        ]
        ms.actions_json = [
            {"name": a.name, "description": a.description}
            for a in MonsterActionTemplate.objects.filter(monster=ms).order_by(
                "sort_order", "name"
            )
        ]
        ms.reactions_json = [
            {"name": r.name, "description": r.description}
            for r in MonsterReaction.objects.filter(monster=ms).order_by("name")
        ]
        ms.legendary_actions_json = [
            {"name": la.name, "description": la.description, "cost": la.cost}
            for la in LegendaryActionTemplate.objects.filter(monster=ms).order_by(
                "sort_order", "cost", "name"
            )
        ]
        ms.lair_actions_json = [
            {"description": la.description}
            for la in LairActionTemplate.objects.filter(monster=ms).order_by("sort_order")
        ]

        try:
            sc = MonsterSpellcasting.objects.get(monster=ms)
            spells = {}
            for level in sc.levels.order_by("level"):
                if level.level == "cantrips":
                    spells["cantrips"] = level.spells
                else:
                    spells[level.level] = {
                        "slots": level.slots,
                        "spells": level.spells,
                    }
            ms.spellcasting_json = {
                "ability": sc.ability,
                "save_dc": sc.save_dc,
                "attack_bonus": sc.attack_bonus,
                "spells": spells,
            }
        except MonsterSpellcasting.DoesNotExist:
            ms.spellcasting_json = {}

        ms.save()


class Migration(migrations.Migration):
    dependencies = [
        ("bestiary", "0005_normalize_remaining_json"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
```

**Step 2: Run the migration against the dev database**

Run: `doppler run -- uv run python manage.py migrate bestiary`
Expected: Migration applies successfully.

**Step 3: Commit**

```bash
git add bestiary/migrations/0006_migrate_remaining_json.py
git commit -m "refactor: data migration for remaining JSON fields to relational tables"
```

---

### Task 3: Drop old JSON fields

**Files:**
- Modify: `bestiary/models/monsters.py`

**Step 1: Remove the 6 `_json` field definitions from MonsterSettings**

Delete the following field definitions from the `MonsterSettings` class:
- `traits_json`
- `actions_json`
- `reactions_json`
- `legendary_actions_json`
- `lair_actions_json`
- `spellcasting_json`

**Step 2: Run makemigrations**

Run: `doppler run -- uv run python manage.py makemigrations bestiary`

This should generate migration `0007` with `RemoveField` operations for all 6 fields.

**Step 3: Commit**

```bash
git add bestiary/models/monsters.py bestiary/migrations/0007_*.py
git commit -m "refactor: drop remaining JSON fields from MonsterSettings"
```

---

### Task 4: Update fixtures

**Files:**
- Modify: `bestiary/fixtures/monsters.yaml`
- Modify: `bestiary/fixtures/monster_attributes.yaml`

**Step 1: Remove JSON data from monsters.yaml**

For every `bestiary.monstersettings` entry in `monsters.yaml`, remove these fields:
- `traits`
- `actions`
- `reactions`
- `legendary_actions`
- `lair_actions`
- `spellcasting`

Keep: `legendary_action_count` and `has_lair` (these are regular model fields, not JSONFields).

Update the file header comment to note the additional data moved.

**Step 2: Add relational data to monster_attributes.yaml**

Append sections for each new model type to `monster_attributes.yaml`, using the exact data from the current `monsters.yaml` JSON. Follow the existing style in that file. The sections are:

1. **MonsterTrait** entries — for each monster with non-empty `traits`
2. **MonsterActionTemplate** entries — for each action (note: only populate `name`, `description`, `sort_order`; leave structured fields like `attack_bonus` etc. at defaults since the JSON data only had name+description)
3. **MonsterReaction** entries — for each monster with non-empty `reactions`
4. **LegendaryActionTemplate** entries — for each monster with non-empty `legendary_actions`
5. **LairActionTemplate** entries — for each monster with non-empty `lair_actions`
6. **MonsterSpellcasting** entries — for Mage and Lich
7. **MonsterSpellcastingLevel** entries — for each spell level of Mage and Lich

Natural key references: Use the `monster` field as a natural key (the MonsterSettings name, e.g., `Wolf`). For `MonsterSpellcastingLevel`, reference the spellcasting entry via a list natural key `[MonsterName]`.

**Step 3: Commit**

```bash
git add bestiary/fixtures/monsters.yaml bestiary/fixtures/monster_attributes.yaml
git commit -m "refactor: move remaining JSON data to relational fixture entries"
```

---

### Task 5: Run full test suite and verify

**Step 1: Run pre-commit checks**

Run: `pre-commit run --all-files`
Expected: All checks pass.

**Step 2: Run the full test suite**

Run: `doppler run -- uv run poe test`
Expected: All tests pass, including:
- `TestMonsterSettingsFixture::test_special_traits` — Wolf traits via `@cached_property`
- `TestMonsterSettingsFixture::test_actions` — Ogre actions via `@cached_property`
- `TestMonsterSettingsFixture::test_legendary_actions` — Dragon legendary actions
- `TestMonsterSettingsFixture::test_legendary_action_costs` — `a.get("cost")` on dict
- `TestMonsterSettingsFixture::test_lair_actions` — Lich lair actions
- `TestMonsterSettingsFixture::test_spellcasting` — Mage ability/DC/bonus
- `TestMonsterSettingsFixture::test_spellcasting_spells` — Lich spell lists

**Step 3: Run tests with coverage**

Run: `doppler run -- uv run poe test-cov`
Expected: Coverage maintained or improved.

**Step 4: Fix any failures and commit**

If tests fail, investigate and fix. Common issues:
- `values()` returns `None` instead of missing key for nullable fields — tests using `.get()` should still work since dicts from `values()` include all requested keys
- `sort_order` ordering may differ from JSON insertion order — verify fixture sort_order matches
- Spellcasting `@cached_property` may hit `RelatedObjectDoesNotExist` — the `try/except` handles this

---

### Task 6: Update documentation and final commit

**Files:**
- Modify: `CHANGELOG.md`

**Step 1: Update CHANGELOG.md**

Add under `## Unreleased` > `### Changed`:

```markdown
* Normalized remaining MonsterSettings JSON fields (traits, actions, reactions, legendary_actions, lair_actions, spellcasting) into relational tables
  - Added `MonsterSpellcasting` and `MonsterSpellcastingLevel` models
  - Backward-compatible `@cached_property` methods preserve existing dict/list interfaces
  - Updated fixtures to use relational entries
```

**Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for remaining JSON field normalization"
```

---

## Key Risks and Mitigations

| Risk | Mitigation |
|---|---|
| `values()` dict keys don't match JSON keys | Tests verify exact same access patterns (`t["name"]`, `a.get("cost")`) |
| Fixture natural keys not found | `MonsterSettings` uses `name` as PK — natural key references work directly |
| `MonsterSpellcastingLevel` natural key serialization | Use `[MonsterName]` list format for FK to `MonsterSpellcasting` |
| Migration data loss | Reversible data migration with `backwards()` function |
| Template `action.attack_bonus is not None` check | `values()` includes all requested fields, nullable fields return `None` |
