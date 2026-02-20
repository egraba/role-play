# App Split Test Migration Design

**Date**: 2026-02-18
**Branch**: refactor/complete-app-split

## Problem

When `bestiary`, `equipment`, and `magic` were split out of the `character` app, their models moved but their tests did not. The result:

- `bestiary/tests/`, `equipment/tests/`, `magic/tests/` are empty (only `__init__.py`)
- Tests for these apps live in `character/tests/models/` and `character/tests/utils/`
- Factories for all three apps live in `character/tests/factories.py`
- `magic/fixtures/spells.yaml` and `magic/fixtures/spell_effects.yaml` are never loaded (missing from root `conftest.py`)

## Goal

Complete the app split by moving tests and factories to their correct homes, with zero breakage to existing character tests.

## Design

### Factory Split (Option: Move + Re-export)

Create per-app factory files. `character/tests/factories.py` becomes a re-export aggregator so existing character test imports are unchanged.

**New files:**
- `bestiary/tests/factories.py` — monster-related factories
- `equipment/tests/factories.py` — equipment and magic item factories
- `magic/tests/factories.py` — spell, spell effect, and spell slot factories

**Modified:**
- `character/tests/factories.py` — replaces factory class bodies with imports from the new locations; character-specific factories (`CharacterFactory`, etc.) remain here

### Test File Migration

| From | To |
|---|---|
| `character/tests/models/test_monsters.py` | `bestiary/tests/models/test_monsters.py` |
| `character/tests/models/test_equipment.py` | `equipment/tests/models/test_equipment.py` |
| `character/tests/models/test_magic_items.py` | `equipment/tests/models/test_magic_items.py` |
| `character/tests/utils/test_equipment_parsers.py` | `equipment/tests/utils/test_equipment_parsers.py` |
| `character/tests/models/test_spells.py` | `magic/tests/models/test_spells.py` |
| `character/tests/models/test_spell_effects.py` | `magic/tests/models/test_spell_effects.py` |

Original files deleted after move.

### Fixture Gap Fix

Add to root `conftest.py` FIXTURES list (after equipment fixtures):

```python
"magic/fixtures/spells.yaml",
"magic/fixtures/spell_effects.yaml",
```

## Key Constraints

- `character/tests/factories.py` must continue to export all names it currently exports (backward compat)
- Moved test files already import from `bestiary.*`, `equipment.*`, `magic.*` — no import changes expected
- Magic fixtures load after equipment (no FK dependency, but keep order consistent)
- All tests must pass after migration: `doppler run -- uv run poe test`

## Outcome

Each app is self-contained: its models, fixtures, and tests all live within its own directory. `character/` no longer knows about the internals of split apps.
