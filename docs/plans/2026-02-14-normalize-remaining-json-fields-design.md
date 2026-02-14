# Normalize Remaining MonsterSettings JSON Fields

**Date**: 2026-02-14
**Status**: Approved
**Relates to**: PR #446 (normalized 9 attribute JSONFields)

## Context

PR #446 normalized 9 simple attribute JSONFields on `MonsterSettings` (speed, saving_throws, skills, senses, damage relations, condition immunities, languages) into relational tables using a 3-step migration pattern. Six complex JSONFields remain:

| JSONField | Relational model exists? | Template usage | Test usage |
|---|---|---|---|
| `traits` | `MonsterTrait` | Yes (name, description) | Yes (dict access) |
| `actions` | `MonsterActionTemplate` | Yes (name, description, attack_bonus, damage_dice) | Yes (dict access) |
| `reactions` | `MonsterReaction` | Yes (name, description) | No |
| `legendary_actions` | `LegendaryActionTemplate` | Yes (name, description, cost) | Yes (dict access) |
| `lair_actions` | `LairActionTemplate` | No | Yes (length check) |
| `spellcasting` | **None** | No | Yes (nested dict access) |

## Design

### Approach

Follow the exact same pattern as PR #446:

1. Rename the 6 JSONFields with `_json` suffix
2. Add `@cached_property` methods returning the same dict/list interface
3. Data migration copying JSON data into relational tables
4. Drop the old `_json` columns
5. Update fixtures to remove JSON data, add relational entries

### Backward-compatible properties

Each property uses `.values()` to return list-of-dicts matching the current JSON contract. Templates and tests require zero changes.

```python
@cached_property
def traits(self) -> list[dict]:
    return list(self.trait_templates.values("name", "description").order_by("sort_order", "name"))

@cached_property
def actions(self) -> list[dict]:
    return list(self.action_templates.values(
        "name", "description", "attack_bonus", "damage_dice"
    ).order_by("sort_order", "name"))

@cached_property
def reactions(self) -> list[dict]:
    return list(self.reaction_templates.values("name", "description").order_by("name"))

@cached_property
def legendary_actions(self) -> list[dict]:
    return list(self.legendary_action_templates.values(
        "name", "description", "cost"
    ).order_by("sort_order", "cost", "name"))

@cached_property
def lair_actions(self) -> list[dict]:
    return list(self.lair_action_templates.values("description").order_by("sort_order"))

@cached_property
def spellcasting(self) -> dict:
    # Reconstruct the nested dict from MonsterSpellcasting + MonsterSpellcastingLevel
```

### New model: MonsterSpellcasting

```python
class MonsterSpellcasting(models.Model):
    monster = models.OneToOneField(MonsterSettings, on_delete=CASCADE, related_name="spellcasting_entry")
    ability = models.CharField(max_length=3)   # "INT", "WIS", "CHA"
    save_dc = models.PositiveSmallIntegerField()
    attack_bonus = models.SmallIntegerField()

class MonsterSpellcastingLevel(models.Model):
    spellcasting = models.ForeignKey(MonsterSpellcasting, on_delete=CASCADE, related_name="levels")
    level = models.CharField(max_length=10)    # "cantrips", "1st", "2nd", ...
    slots = models.PositiveSmallIntegerField(default=0)
    spells = models.JSONField(default=list)    # ["fire bolt", "light"] - just name strings
```

### Migration sequence

| Migration | Purpose |
|---|---|
| `0005_normalize_remaining_json` | Rename 6 fields with `_json` suffix, create `MonsterSpellcasting` + `MonsterSpellcastingLevel` tables |
| `0006_migrate_remaining_json` | Data migration: JSON data into relational tables |
| `0007_drop_remaining_json` | Remove the 6 `_json` columns |

### Fixture changes

- Remove JSON data (traits, actions, reactions, legendary_actions, lair_actions, spellcasting) from `monsters.yaml`
- Add relational entries to `monster_attributes.yaml` for: `MonsterTrait`, `MonsterActionTemplate`, `MonsterReaction`, `LegendaryActionTemplate`, `LairActionTemplate`, `MonsterSpellcasting`, `MonsterSpellcastingLevel`
