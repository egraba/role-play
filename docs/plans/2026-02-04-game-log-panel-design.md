# Game Log Panel Design

## Overview

A real-time game log panel that displays dice rolls, combat actions, spell casts, player chat, and DM announcements with filtering capabilities.

## Requirements

- Display all game events in a persistent sidebar
- Color-code entries by category
- Filter by event type and character
- Load recent history on connect
- Stream new events via WebSocket
- Expandable entries for details

## UI Design

### Panel Structure

```
┌─────────────────────────┐
│ GAME LOG          [=]   │  ← Header with collapse toggle
├─────────────────────────┤
│ 🎲  ⚔️  ✨  💬  📢      │  ← Category filter toggles
├─────────────────────────┤
│ Characters: [dropdown▼] │  ← Multi-select character filter
├─────────────────────────┤
│                         │
│   (scrollable log)      │  ← Event entries
│                         │
│   ↓ 3 new events        │  ← New events indicator
└─────────────────────────┘
```

- Fixed-width right sidebar (320px)
- Full height of game content area
- All filter toggles active by default

### Visual Styling

**Category Colors:**

| Category | Color | Hex | Events |
|----------|-------|-----|--------|
| Rolls | Blue | `#5b9bd5` | Dice rolls, ability checks, saving throws |
| Combat | Red | `#e05252` | Attacks, damage, initiative, turns |
| Spells | Purple | `#a855f7` | Spell casts, effects, concentration |
| Chat | Gray | `#9ca3af` | Player messages |
| DM | Gold | `#d4a857` | Master messages, quest updates |

**Entry Layout:**

```
┌─ Collapsed ─────────────────────────┐
│ [color bar] 10:42  Thorin           │
│             Rolled 18 on Athletics  │
└─────────────────────────────────────┘

┌─ Expanded ──────────────────────────┐
│ [color bar] 10:42  Thorin           │
│             Rolled 18 on Athletics  │
│  ┌─ details ─────────────────────┐  │
│  │ Roll: 1d20 + 5                │  │
│  │ Dice: [14]                    │  │
│  │ Modifier: +5 (STR)            │  │
│  │ DC: 15 ✓ Success              │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

- 4px left color bar indicates category
- Click anywhere to toggle expand/collapse

## Event Categorization

| Category | Event Types |
|----------|-------------|
| Rolls | `DICE_ROLL`, `ABILITY_CHECK_RESULT`, `SAVING_THROW_RESULT`, `COMBAT_INITIATIVE_RESULT` |
| Combat | `COMBAT_STARTED`, `TURN_STARTED`, `TURN_ENDED`, `ROUND_ENDED`, `COMBAT_ENDED`, `ACTION_TAKEN`, `HP_DAMAGE`, `HP_HEAL`, `HP_TEMP`, `HP_DEATH_SAVE` |
| Spells | `SPELL_CAST`, `SPELL_DAMAGE_DEALT`, `SPELL_HEALING_RECEIVED`, `SPELL_CONDITION_APPLIED`, `SPELL_SAVING_THROW`, `CONCENTRATION_*` |
| Chat | `MESSAGE` (from players) |
| DM | `MESSAGE` (from master), `QUEST_UPDATE`, `GAME_START` |

**Note:** Messages are categorized as DM if the author is the game's Master.

## Data Flow

### Initial Load

1. On WebSocket connect, fetch `GET /game/<game_id>/log/`
2. Returns last 50 events with: id, type, category, timestamp, author, message, details
3. Populate log oldest-first (newest at bottom)

### Real-time Updates

Enhance existing WebSocket payload with new fields:

```json
{
    "type": "spell.cast",
    "category": "spells",
    "username": "Thorin",
    "character_id": 42,
    "character_name": "Thorin",
    "date": "2024-01-15T10:42:00",
    "message": "Cast Fireball at 3rd level",
    "details": {
        "spell_name": "Fireball",
        "slot_level": 3,
        "targets": ["Goblin 1", "Goblin 2"]
    }
}
```

### Reconnection

- Fetch history again on reconnect
- Deduplicate by event ID

## Scroll Behavior

**Smart auto-scroll:**
- If at bottom (within 50px): auto-scroll on new events
- If scrolled up: show "↓ N new events" indicator
- Click indicator to jump to bottom

**Performance:**
- Keep max ~200 entries in DOM
- Render expanded details on demand

## Implementation Files

### Backend

| File | Change |
|------|--------|
| `game/views.py` | Add `GameLogView` |
| `game/urls.py` | Add `/game/<game_id>/log/` route |
| `game/serializers.py` | Add `GameLogEventSerializer` |
| `game/services.py` | Enhance `send_to_channel()` with category, character_id, details |
| `game/constants/log_categories.py` | Event type → category mapping |

### Frontend

| File | Change |
|------|--------|
| `game/templates/game/game.html` | Add log panel to layout |
| `game/templates/game/partials/game_log.html` | Log panel partial |
| `game/static/game/css/game_log.css` | Panel styles |
| `game/static/game/js/game_log.js` | Log class with filtering, scroll, WebSocket |

## Expanded Details by Category

| Category | Details Shown |
|----------|---------------|
| Rolls | Dice notation, individual dice, modifier breakdown, DC, pass/fail |
| Combat | Action type, target, damage/healing, resulting HP |
| Spells | Spell name, slot level, targets, effects |
| Chat/DM | Full message only |
