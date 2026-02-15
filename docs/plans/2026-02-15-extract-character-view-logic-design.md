# Extract Business Logic from Character Views

## Problem

`character/views/spells.py` (430 lines) and `character/views/character.py` (422 lines)
contain domain logic that should live in a service module:

- Spell slot visualization, filtering, grouping, quick-cast computation
- Spell casting orchestration (find spell, consume slot, start concentration)
- Character sheet data building (abilities, skills, saving throws, attack bonuses)
- Character creation orchestration (builder pipeline + equipment handling)

This logic is untestable without HTTP request/response machinery and violates the
separation established by `game/services.py`.

## Approach

Create `character/services.py` with service classes. Views become thin HTTP
orchestrators: parse request, call service, render template.

## Service Design

### SpellsPanelService

Query and command service for spell-related operations.

```python
class SpellsPanelService:
    @staticmethod
    def get_spells_panel_data(
        character: Character,
        *,
        level_filter: int | None = None,
        school_filter: str | None = None,
        concentration_filter: bool | None = None,
        search_query: str | None = None,
    ) -> dict: ...

    @staticmethod
    def cast_spell(
        character: Character,
        spell_name: str,
        cast_level: int,
    ) -> SpellCastResult: ...

    @staticmethod
    def restore_all_slots(character: Character) -> None: ...
```

`get_spells_panel_data` extracts the ~170-line `get_spells_context()` mixin method.
`cast_spell` extracts spell-finding + slot-consuming + concentration logic from `CastSpellView`.
`restore_all_slots` extracts the restoration loop from `RestoreAllSlotsView`.

### CharacterSheetService

Query service for character detail page data.

```python
class CharacterSheetService:
    @staticmethod
    def get_character_sheet_data(character: Character) -> dict: ...
```

Extracts the ~140-line data-building block from `CharacterDetailView.get_context_data()`.

### CharacterCreationService

Command service for wizard completion.

```python
class CharacterCreationService:
    @staticmethod
    def create_character(
        user: User,
        *,
        name: str,
        species: Species,
        klass: Class,
        abilities: dict[str, int],
        background: Background,
        skills: list[str],
        equipment: list[str],
    ) -> Character: ...
```

Extracts the builder pipeline + equipment handling from `CharacterCreateView.done()`.
Eliminates the `MockAbilityForm` hack by accepting a plain dict of ability scores.

## Data Types

```python
@dataclass
class SpellCastResult:
    success: bool
    message: str
    spell_name: str | None = None
    cast_level: int | None = None
```

## View Changes

### character/views/spells.py (~430 -> ~150 lines)

- `SpellsPanelMixin.get_spells_context()` delegates to `SpellsPanelService.get_spells_panel_data()`
- `CastSpellView.post()` parses form, calls `SpellsPanelService.cast_spell()`, renders template
- `RestoreAllSlotsView.post()` calls `SpellsPanelService.restore_all_slots()`, renders template
- UseSpellSlotView, RestoreSpellSlotView, BreakConcentrationView unchanged (already thin)

### character/views/character.py (~422 -> ~260 lines)

- `CharacterDetailView.get_context_data()` delegates to `CharacterSheetService`
- `CharacterCreateView.done()` delegates to `CharacterCreationService`
- Wizard step methods (get_template_names, get_form_initial, etc.) stay in view

## Testing

Service methods are independently testable with model factories.
View tests simplify to: parse request -> delegate to service -> render response.

## Files Changed

- `character/services.py` (new)
- `character/views/spells.py` (modified)
- `character/views/character.py` (modified)
