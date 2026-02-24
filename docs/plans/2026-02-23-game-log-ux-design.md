# Game Log UX Design

**Goal:** Fix broken filtering and deliver a full UX polish pass on the game log panel.

**Architecture:** All changes are confined to `game-log.css` and `game-log.js`. No backend
changes required — the serialized event data already includes `category`, `character_id`, and
`details` fields.

**Tech Stack:** Vanilla JS (GameLog class), CSS custom properties from rpg-styles.css design
system, SVG icons via `rpg-icon` filter system.

---

## Bug Fixes

### CSS/JS class name mismatch
`game-log.css` uses `event-entry`, `event-sender`, `event-meta` — class names from a previous
version. The JS generates `log-entry`, `log-entry-author`, `log-entry-header`, etc. Result:
entries have no styling and `.log-entry.hidden { display: none }` doesn't exist, so filtering
has no visual effect.

**Fix:** Rewrite the entry section of `game-log.css` to match the class names the JS generates.

### Character filter include-list logic
`filters.characters` is intended as an include-list (empty = show all), but the checkbox handler
adds IDs when unchecked and the filter check treats the set as an exclude-list. These two halves
contradict each other.

**Fix:** Make checkbox handler and filter check consistent — both use include-list semantics:
- Uncheck a character → add all *other* checked characters to the set
- Check a character → add to set; if all are now checked, clear set (= show all)
- Filter: if set non-empty, hide events whose `character_id` is not in set (events without
  `character_id` — DM/system — always show)

---

## Entry Styling

Each `.log-entry` gets a 3px left bar (`.log-entry-bar`) colored by category:
- Rolls: `var(--accent)` (gold)
- Combat: `var(--red)`
- Spells: `#9b59b6` (purple)
- Chat: `var(--text-muted)`
- DM: `var(--green)`, message text italic + muted

Entries with details (already wired to toggle `.expanded` on click) get a `▶` indicator in
the header that rotates to `▼` when expanded. Details panel gets an inset background, with
`.success` (green) and `.failure` (red) value spans.

---

## Filter Bar

Category buttons replace emoji with SVG icons + text labels:

| Category | Icon                    | Label   |
|----------|-------------------------|---------|
| Rolls    | actions/roll.svg        | Rolls   |
| Combat   | actions/attack.svg      | Combat  |
| Spells   | actions/cast-spell.svg  | Spells  |
| Chat     | actions/persuade.svg    | Chat    |
| DM       | ui/info.svg             | DM      |

Icons use `rpg-icon rpg-icon-sm`. Inactive: dim (`var(--text-muted)`). Active: gold via
`filter-toggle.active` (border-bottom + full brightness).

Character filter button gets `border-bottom: 2px solid var(--accent)` when a filter is active
(`.active` class toggled in JS).
