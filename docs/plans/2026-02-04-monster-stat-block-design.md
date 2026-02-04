# Monster Stat Block Component Design

## Overview

A Django template partial that renders a D&D 5e monster stat block in the official format, designed for the DM dashboard. Features a parchment aesthetic with gold RPGUI framing and interactive quick-roll buttons.

## File Location

```
game/templates/game/partials/monster_stat_block.html
```

## Visual Layout

```
┌─────────────────────────────────────────────┐
│ ▌ GOBLIN                                    │  ← Name (red accent bar)
│   Small Humanoid, Neutral Evil              │  ← Type line (italic)
├─────────────────────────────────────────────┤
│ Armor Class 15 (leather armor, shield)      │
│ Hit Points 7 (2d6)              [Roll HP]   │
│ Speed 30 ft.                                │
├─────────────────────────────────────────────┤
│ STR  DEX  CON  INT  WIS  CHA                │
│  8   14   10    10   8   8                  │
│ (-1) (+2) (+0) (+0) (-1) (-1)               │  ← Clickable modifiers
├─────────────────────────────────────────────┤
│ Skills Stealth +6                           │
│ Senses darkvision 60 ft., passive Per. 9    │
│ Languages Common, Goblin                    │
│ Challenge 1/4 (50 XP)   Prof. Bonus +2      │
├─────────────────────────────────────────────┤
│ ACTIONS                                     │
│ Scimitar. Melee Weapon Attack...   [Roll]   │
│ Shortbow. Ranged Weapon Attack...  [Roll]   │
└─────────────────────────────────────────────┘
```

## Template Context

```python
{
    "monster": MonsterSettings,  # or Monster instance for combat
    "game": Game,                # for roll endpoint URLs
    "show_roll_buttons": True,   # toggle interactive elements
}
```

## Data Mapping

| Stat Block Field | Model Field(s) |
|------------------|----------------|
| Name | `monster.name` |
| Type line | `monster.size`, `monster.creature_type`, `monster.subtype`, `monster.alignment` |
| AC | `monster.ac`, `monster.ac_type` |
| HP | `monster.hp_average`, `monster.hit_dice` |
| Speed | `monster.speed` (JSON dict) |
| Abilities | `monster.strength` ... `monster.charisma` + computed modifiers |
| Saves | `monster.saving_throws` (JSON dict) |
| Skills | `monster.skills` (JSON dict) |
| Damage immunities/resistances/vulnerabilities | JSON lists |
| Condition immunities | `monster.condition_immunities` (JSON list) |
| Senses | `monster.senses` (JSON dict) |
| Languages | `monster.languages` (JSON list) |
| CR / XP | `monster.challenge_rating`, `monster.xp` (property) |
| Traits | `monster.traits` (JSON) or `monster.trait_templates.all()` |
| Actions | `monster.actions` (JSON) or `monster.action_templates.all()` |
| Reactions | `monster.reactions` (JSON) |
| Legendary Actions | `monster.legendary_actions` (JSON) |

## Interactive Elements

### Quick-Roll Buttons

| Element | Dice Expression | Label |
|---------|-----------------|-------|
| Ability modifier | `1d20 + {mod}` | "{Monster} {Ability} Check" |
| Saving throw | `1d20 + {save}` | "{Monster} {Ability} Save" |
| Attack roll | `1d20 + {attack_bonus}` | "{Monster} {Action} Attack" |
| Damage roll | `{damage_dice}` | "{Monster} {Action} Damage" |
| Hit Dice | `{hit_dice}` | "{Monster} HP Roll" |

### HTMX Integration

```html
<button class="stat-roll-btn"
        hx-post="{% url 'dice-roll' game.id %}"
        hx-vals='{"dice": "1d20+5", "label": "Goblin Scimitar Attack"}'
        hx-target="#combat-log"
        hx-swap="afterbegin">
    ⚄
</button>
```

## CSS Design

### Color Palette
- Parchment background: `#f4e4bc` to `#e8d5a3` gradient
- Text: `#1a1a1a` (dark brown-black)
- Red accent bars: `#7a200d` to `#a0522d`
- Gold frame: `var(--color-primary)` (`#d4af37`)
- Roll button accent: `#8b4513` (saddle brown)

### Key Classes
- `.monster-stat-block` - Main container
- `.stat-block-header` - Name and type
- `.stat-block-divider` - Red gradient divider
- `.stat-block-abilities` - 6-column ability grid
- `.stat-block-property` - Label + value pairs
- `.stat-block-section` - Traits/Actions/etc headers
- `.stat-roll-btn` - Inline dice roll button

## Sections Rendered

1. **Header** - Name (bold, larger) + type line (italic)
2. **Divider** (red gradient)
3. **Core Stats** - AC, HP (with roll), Speed
4. **Divider**
5. **Ability Scores** - 6-column grid with scores and modifiers
6. **Divider**
7. **Properties** - Saves, skills, damage mods, condition immunities, senses, languages, CR
8. **Divider**
9. **Traits** (if any) - Name in bold italic, description
10. **Actions** - "ACTIONS" header, each action with roll buttons
11. **Reactions** (if any) - "REACTIONS" header
12. **Legendary Actions** (if any) - "LEGENDARY ACTIONS" header with preamble

## Responsive Behavior

- Min-width: 280px (sidebar-friendly)
- Max-width: 400px (doesn't sprawl on wide screens)
- Ability grid collapses to 3x2 on narrow screens
- Roll buttons remain accessible on mobile

## Usage Example

```django
{% include "game/partials/monster_stat_block.html" with monster=goblin game=game show_roll_buttons=True %}
```
