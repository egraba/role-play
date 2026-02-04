# DM Dashboard Design

A dedicated dashboard page for Dungeon Masters to manage game sessions with full visibility and control.

## Overview

**Route**: `/game/<id>/dm/`

**Access**: Game master only (403 for players)

**Layout**: Fixed 2-column, 3-row grid filling the viewport

```
┌─────────────────────┬─────────────────────┐
│   Party Overview    │  Initiative Tracker │
├─────────────────────┼─────────────────────┤
│   Monster Quick-Add │  Encounter Manager  │
├─────────────────────┼─────────────────────┤
│   Session Notes     │   Secret Rolls      │
└─────────────────────┴─────────────────────┘
```

**Real-time sync**: Connects to existing WebSocket channel (`game_{id}_events`) for automatic updates.

---

## Panel Specifications

### 1. Party Overview

At-a-glance view of all player characters.

**Display per character**:
- Name (linked to character sheet)
- HP bar with visual + numeric display, color-coded by health percentage
- Active conditions as icons (using existing condition icon set)
- Concentration indicator with spell name on hover
- Location text field (editable inline by DM)

**Interactivity**:
- Click name → character sheet (new tab)
- Click HP → damage/heal modal
- Click location → inline edit, saves via HTMX

**New field required**: `Character.location` (CharField, blank=True)

### 2. Initiative Tracker

Full combat control, extending existing `initiative_tracker.html`.

**Existing features** (retained):
- Round counter
- Ordered combatant list with initiative, name, mini HP bar, conditions
- Current turn highlight
- Next Turn / End Combat buttons

**New additions**:
- Edit initiative value inline (click to edit)
- Remove combatant button (X icon)
- Add to combat button (integrates with Monster Quick-Add)

**Implementation**: Pass `is_dashboard=True` context flag to show additional controls.

### 3. Monster Quick-Add

Search and select monsters from `MonsterSettings` database.

**Interface**:
- Type-ahead search box
- Results list showing: Name, CR, HP, AC
- "Add to Combat" button per result (when combat active)
- "Add to Template" button per result (for encounter builder)

**Monster preview on hover**: AC, HP, Speed, ability scores, notable traits

**Add to combat flow**:
1. Click "Add to Combat"
2. Modal: quantity and initiative method (roll/manual)
3. Create `Monster` instance(s) with auto-naming ("Goblin 1", "Goblin 2")
4. Create `Fighter` record(s) linking to combat
5. Broadcast WebSocket event to refresh tracker

### 4. Encounter Manager

Create, save, and load pre-built encounter templates.

**New models**:

```python
class EncounterTemplate(models.Model):
    name = models.CharField(max_length=100)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class EncounterTemplateMonster(models.Model):
    template = models.ForeignKey(EncounterTemplate, on_delete=models.CASCADE, related_name="monsters")
    monster_settings = models.ForeignKey(MonsterSettings, on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField(default=1)
```

**Interface**:
- Saved templates list with name and monster summary
- "New Template" button → inline form
- Template builder: add monsters, adjust counts, remove
- "Load into Combat" button per template

**Load flow**:
1. Click "Load into Combat"
2. Create `Combat` instance
3. Create `Monster` and `Fighter` instances per template entry
4. Prompt for initiative method
5. Begin initiative rolling or start combat

### 5. Session Notes

Simple scratchpad for DM notes during play.

**New model**:

```python
class SessionNote(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name="session_note")
    content = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Interface**:
- Large textarea (15-20 visible lines)
- Auto-save on blur or after 2s inactivity (debounced HTMX)
- "Last saved" timestamp display
- Monospace font, dark theme

**Persistence**: One note document per game, persists across sessions.

### 6. Secret Rolls

Roll Perception and Insight checks secretly for player characters.

**Interface**:
- Character dropdown (all characters in game)
- "Perception" and "Insight" buttons
- Results log (scrollable)

**Roll display format**:
```
[14:32] Thorin - Perception: 18 (d20:14 + 4)
```

**Calculation**:
- Fetch character's Wisdom modifier
- Check Perception/Insight proficiency via `Skill` model
- Add proficiency bonus if applicable
- Roll d20 + total modifier

**Visibility**: DM only. Not broadcast via WebSocket, not stored in Event log.

**Storage**: Browser session storage (clears on close). No database persistence.

---

## File Changes

### New Files

| File | Purpose |
|------|---------|
| `game/views/dm_dashboard.py` | Dashboard view and panel endpoints |
| `game/templates/game/dm_dashboard.html` | Main dashboard template |
| `game/templates/game/partials/dm_party.html` | Party overview panel |
| `game/templates/game/partials/dm_initiative.html` | Initiative tracker variant |
| `game/templates/game/partials/dm_monsters.html` | Monster quick-add panel |
| `game/templates/game/partials/dm_encounters.html` | Encounter manager panel |
| `game/templates/game/partials/dm_notes.html` | Session notes panel |
| `game/templates/game/partials/dm_secret_rolls.html` | Secret rolls panel |
| `game/models/encounters.py` | EncounterTemplate, EncounterTemplateMonster |
| `game/models/notes.py` | SessionNote |
| `game/forms/dm_dashboard.py` | Dashboard-specific forms |

### Modified Files

| File | Change |
|------|--------|
| `game/urls.py` | Add dashboard routes |
| `game/models/__init__.py` | Export new models |
| `game/templates/game/game.html` | Add "Open DM Dashboard" link |
| `character/models/character.py` | Add `location` field |
| `game/models/combat.py` | Support Monster as Fighter |

---

## URL Structure

| Route | Purpose |
|-------|---------|
| `/game/<id>/dm/` | Main dashboard page |
| `/game/<id>/dm/party/` | Party panel partial (HTMX refresh) |
| `/game/<id>/dm/party/<char_id>/location/` | Update character location |
| `/game/<id>/dm/monsters/search/` | Monster search endpoint |
| `/game/<id>/dm/monsters/add-to-combat/` | Add monster to active combat |
| `/game/<id>/dm/encounters/` | List encounter templates |
| `/game/<id>/dm/encounters/create/` | Create new template |
| `/game/<id>/dm/encounters/<id>/` | Template detail/edit |
| `/game/<id>/dm/encounters/<id>/load/` | Load template into combat |
| `/game/<id>/dm/notes/` | Save notes endpoint |
| `/game/<id>/dm/rolls/secret/` | Execute secret roll |

---

## Technical Notes

### WebSocket Integration

The dashboard connects to the same `game_{id}_events` WebSocket channel. Combat events trigger HTMX refreshes:
- `initiative-updated` → refreshes Initiative Tracker and Party Overview
- `hp.*` events → refreshes Party Overview
- `combat.*` events → refreshes Initiative Tracker

### HTMX Patterns

Each panel is a partial template that can be independently refreshed:
```html
<div hx-get="{% url 'dm-party' game.id %}"
     hx-trigger="load, initiative-updated from:body"
     hx-swap="innerHTML">
</div>
```

### Access Control

All dashboard views use:
```python
class DMDashboardMixin(UserPassesTestMixin, GameContextMixin):
    def test_func(self):
        return self.is_user_master()
```

### No Breaking Changes

All additions are additive. Existing game flow, player views, and combat mechanics remain unchanged.
