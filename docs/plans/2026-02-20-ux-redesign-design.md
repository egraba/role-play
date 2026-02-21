# UX Redesign Design — 2026-02-20

## Overview

Full UX redesign of the role-play virtual tabletop. The goal is to replace the current dark-fantasy (rpgui-derived) aesthetic with a clean, flat dark mode — minimal components, no decorative chrome, modern SaaS sensibility.

**Scope:** game screen, home page, game list, attack/dice/concentration modals, base chrome (navbar, layout shell).

**Approach:** CSS design system replacement + targeted template restructuring. No new frontend dependencies.

---

## 1. Design System

### CSS Variables

```css
:root {
  --bg:         #111111;
  --bg-surface: #1a1a1a;
  --bg-raised:  #222222;
  --border:     rgba(255, 255, 255, 0.08);
  --text:       #e5e5e5;
  --text-muted: #888888;
  --accent:     #c9a227;   /* muted gold */
  --red:        #c0392b;   /* damage / danger */
  --green:      #27ae60;   /* hit / health */
  --blue:       #2980b9;   /* movement / info */
  --radius:     4px;
}

body {
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  background: var(--bg);
  color: var(--text);
}
```

### Component Vocabulary

| Class | Purpose | Replaces |
|---|---|---|
| `.surface` | Flat container, `bg-surface` + `border` | `rpg-panel` |
| `.btn` | Flat button with border, no gradient | `rpg-btn` |
| `.btn-primary` | Accent-colored border + text | `btn-primary` |
| `.btn-ghost` | Muted border, dimmed text | `btn-defend`, `btn-skill` |
| `.btn-danger` | Red border + text | `btn-attack`, `btn-danger` |
| `.badge` | Inline label (e.g. `HIT`, `YOUR TURN`) | Various inline spans |
| `.divider` | `border-top: 1px solid var(--border)` | `rpg-section` separators |

### Removed

- All `linear-gradient()` backgrounds
- All `box-shadow` with blur > 4px
- All CSS animations: `pulse-glow`, `criticalPulse`, `concentration-glow`, `pulse-border`, `pulse-dot`, `pulse-critical`, `diceRoll`, `fumbleShake`, `criticalText`, `tracker-ready`, `tracker-delay`
- `font-family: Georgia, 'Times New Roman', serif` everywhere
- `letter-spacing` decorative effects
- `text-shadow` glow effects
- Embedded `<style>` blocks in partials — all styles move to `rpg-styles.css`

---

## 2. Base Chrome

### Navbar

- Height: `48px`
- `background: var(--bg)`, `border-bottom: 1px solid var(--border)`
- Font: `system-ui`, `font-size: 14px`
- Brand: one SVG icon + "Role Play" text
- Nav links: text only, no per-link SVG icons
- User dropdown: plain text, no icon on username button

### Layout Shell

- `<main>` provides horizontal padding (`16px` or `24px`), no `.rpg-container` max-width wrapper on simple pages
- Game screen overrides to full-viewport two-column layout (see Section 3)
- Footer: two lines of text, `border-top: 1px solid var(--border)`, no decorative elements

---

## 3. Game Screen Layout

### Structure

Two fixed-height columns filling `calc(100vh - 48px)`, each independently scrollable.

```
┌─ navbar (48px) ──────────────────────────────────────────┐
├──────────────────────────────────────────────────────────┤
│  ┌── Game Log (40%) ──────┐  ┌── Play Area (60%) ───────┐ │
│  │                        │  │                           │ │
│  │  [Game Name]  Round N  │  │  QUEST                    │ │
│  │  ──────────────────    │  │  [quest text]             │ │
│  │                        │  │  ─────────────────────    │ │
│  │  [event stream]        │  │  [message input] [Send]   │ │
│  │  (scrollable)          │  │  [Roll Dice]              │ │
│  │                        │  │  ─────────────────────    │ │
│  │                        │  │  INITIATIVE  Round N      │ │
│  │  ──────────────────    │  │  [combatant list]         │ │
│  │  All  Chat  Combat     │  │  ─────────────────────    │ │
│  │  Dice                  │  │  ACTIONS                  │ │
│  └────────────────────────┘  │  [action economy]         │ │
│                              │  ─────────────────────    │ │
│                              │  CHARACTERS               │ │
│                              │  [character list]         │ │
│                              └───────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Game Log Column (40%)

- `height: calc(100vh - 48px)`, `overflow-y: auto`
- Header: game name + round counter (if in combat), separated by a divider
- Event stream: scrollable, newest events at bottom
- Event row format: `sender / event-type + timestamp` on one line, content indented below
  - System events prefixed with `✦` in `--text-muted`
  - Player messages as plain text
- Filter bar: pinned to bottom, four plain text tabs (`All / Chat / Combat / Dice`), underline-active
- No search bar

### Play Area Column (60%)

- `height: calc(100vh - 48px)`, `overflow-y: auto`
- Sections separated by `.divider`, not nested `.surface` boxes
- Section labels: small uppercase, `--text-muted`, `font-size: 11px`, `letter-spacing: 0.05em`

**Quest section:**
- Plain text block, `white-space: pre-line`
- DM only: small ghost `[Update Quest ▸]` button, right-aligned

**Messaging section:**
- `[input field] [Send]` on one row
- `[Roll Dice]` ghost button below
- Contextual buttons (ability check / saving throw / initiative check) replace the ghost button when a request is active

**Initiative section (combat only):**
- Section header: `INITIATIVE   Round N` + DM controls `[Next Turn] [End Combat]` right-aligned
- Combatant rows: `● (current) | initiative value | name | HP bar | HP text | condition badges`
- Current combatant: name in `--accent` color, `●` dot indicator. No animations.
- HP bar: 8px, green → yellow (≤50%) → red (≤25%). No animation.
- Condition badges: inline text, muted red
- Player turn row only: `[Ready] [Delay]` ghost buttons

**Action panel section (combat only):**
- Four rows: `Action / Bonus / Reaction / Movement`
- Action buttons: flat `.btn`, greyed out (`opacity: 0.35`, `pointer-events: none`) when used
- "Your Turn" badge next to section label, `background: var(--green)`
- Movement: progress bar + `[5 ft] [10 ft] [All]` ghost buttons
- Actions taken: small muted list below movement, same section

**Characters section:**
- Plain list with linked character names
- DM only: `[Invite a User ▸]` ghost button, right-aligned

### Master Controls Integration

DM-only controls are embedded inline within their relevant sections:
- Quest: `[Update Quest ▸]`
- Initiative: `[Next Turn] [End Combat]`
- Messaging: `[Ask for Ability Check]`, `[Initiate Combat]` as ghost buttons below Roll Dice
- Pre-game: `[Start the Game]` replaces the messaging section entirely

### Removed

- `position: fixed` game log overlay
- `margin-right: 360px` hack on `.rpg-container`
- Separate `.dm-controls` section below initiative tracker
- Master's Panel as a separate nested box
- "Back to top" link with unconscious-condition SVGs
- Duplicated game title heading in the main content area
- `location.reload()` for non-combat WebSocket events → targeted HTMX updates

### Responsive (mobile < 768px)

- Stack to single column
- Game log collapses to a bottom drawer, toggled by a fixed tab

---

## 4. Modals

### Shared Modal Shell

- Overlay: `background: rgba(0, 0, 0, 0.6)`
- Box: `background: var(--bg-surface)`, `border: 1px solid var(--border)`, `border-radius: var(--radius)`, `max-width: 420px`, `width: 90vw`
- Header: plain `font-weight: 600` text, no SVG icon
- Close: `×` top-right, `color: var(--text-muted)`, no border
- No `min-width` forcing fixed size on mobile

### Attack Modal (3 steps)

**Step 1 — Setup:**
```
Attack
────────────────────────────
Target    [Goblin (AC 13) ▾]
Weapon    [Longsword (1d8+3, +5) ▾]
Modifier  [Disadvantage] [Normal ✓] [Advantage]
Attack bonus  +5
                  [Cancel] [Roll Attack]
```

**Step 2 — Attack result:**
```
Attack vs Goblin (AC 13)
────────────────────────────
         20         ← large monospace, --accent
  14 + 5 = 20       ← --text-muted
  HIT               ← green badge
                  [Cancel] [Roll Damage]
```
Critical hit: `CRITICAL HIT` badge in `--accent`. Critical miss: `CRITICAL MISS` badge in `--red`. No animations.

**Step 3 — Damage:**
```
Damage
────────────────────────────
  2d8 + 3  =  11 slashing damage
  Goblin: 17 → 6 HP
                  [Cancel] [Apply Damage]
```

**Step 3b — Concentration check:**
```
Concentration check required
────────────────────────────
Goblin must make a DC 10 Constitution
save to maintain Hypnotic Pattern.
          [Later] [Roll Concentration Save]
```

### Dice Roller Modal

```
Roll Dice
────────────────────────────
[d4] [d6] [d8] [d10] [d12] [d20]
Count [1 ▾]   Modifier [+0]

Result: 17
                  [Cancel] [Roll]
```
- Die type: flat toggle buttons, underline-active
- Result: large `--accent` number, no die graphic, no animation

### Concentration Save Modal

```
Concentration Save
────────────────────────────
Kira must make a DC 12 Constitution save
to maintain Blur.

Con modifier   +2
Proficiency    +2
Total          +4

Result: 18
Concentration maintained ✓
                  [Cancel] [Roll Save]
```

---

## 5. Home Page & Game List

### Home Page

**Logged out:**
```
Role Play

A virtual tabletop for D&D 5th Edition (SRD 5.2.1).

[Log in]  [GitHub ↗]
```

**Logged in (with active game):**
```
Welcome back, kira.

[Continue: The Sunken Temple ▸]
[View all games]  [My character]  [Create a game]
```

**Logged in (no active game):**
```
Welcome back, kira.

[View all games]  [My character]  [Create a game]
```

- No marketing bullets, no community section, no icon parade
- All CTAs as flat buttons (`.btn-primary` for primary CTA, `.btn-ghost` for secondary)

### Game List

```
Games
────────────────────────────────────────
Name                  Master    Status     Players
The Sunken Temple     egraba    Ongoing    3
Dragon's Keep         marcus    Prep       1
────────────────────────────────────────
← 1 2 3 →                      [Create a game]
```

- No `.rpg-panel` wrapper around the table
- `border-collapse: collapse`, rows separated by `border-bottom: 1px solid var(--border)`
- "Return to main menu" link removed (navbar handles navigation)

### Other Small Forms

Game start confirmation, quest create, ability check request, user invite — all keep their existing structure. The `.rpg-panel` wrapper simplifies to `.surface`. Buttons become `.btn`.

---

## 6. Files Changed

### Modified

| File | Change |
|---|---|
| `game/static/css/rpg-styles.css` | Full replacement — new design system, layout utilities |
| `game/static/css/game-log.css` | Full replacement — strip decorative styles |
| `game/static/css/quick-reference.css` | Strip decorative styles |
| `game/templates/base.html` | Navbar simplification, font change |
| `game/templates/game/game.html` | Two-column layout, remove floating panel, inline DM controls |
| `game/templates/game/index.html` | Minimal welcome page |
| `game/templates/game/game_list.html` | Strip panel wrapper, clean table |
| `game/templates/game/partials/game_log_panel.html` | New event row format, bottom filter bar |
| `game/templates/game/partials/initiative_tracker.html` | Inline DM controls, remove animations |
| `game/templates/game/partials/action_panel.html` | Four-row layout, remove `<style>` block |
| `game/templates/game/partials/attack_modal.html` | Simplified 3-step flow, remove `<style>` block |
| `game/templates/game/partials/dice_roller_modal.html` | Simplified, remove animation |
| `game/templates/game/partials/concentration_save_modal.html` | Simplified |
| `game/templates/game/partials/quick_reference_panels.html` | Strip decorative styles |
| `game/templates/game/game_start.html` | `.surface` wrapper, flat buttons |
| `game/templates/game/quest_create.html` | `.surface` wrapper, flat buttons |
| `game/templates/game/ability_check_request.html` | `.surface` wrapper, flat buttons |
| `game/templates/game/user_invite.html` | `.surface` wrapper, flat buttons |
| `game/templates/game/user_invite_confirm.html` | `.surface` wrapper, flat buttons |
| `game/templates/game/combat_create.html` | `.surface` wrapper, flat buttons |

### No changes

- All Python files (views, models, consumers, services)
- URL routing
- WebSocket logic (except removing `location.reload()` for non-combat events)
- `game/static/js/game-log.js` — behaviour unchanged, CSS class names updated
- `game/static/js/keyboard-shortcuts.js` — unchanged
- `game/static/js/quick-reference.js` — unchanged
