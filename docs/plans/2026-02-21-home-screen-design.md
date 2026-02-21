# Home Screen Redesign Design

**Goal:** Make the home screen feel substantial and atmospheric for new/anonymous visitors.

**Audience:** New visitors who don't know what Role Play is.

**Tone:** Atmospheric / immersive — dark, evocative, fantasy-world feeling.

---

## Design: Hero + Feature Grid

### Hero section

Centered, max-width 600px, generous padding-top.

```
Role Play

Enter a world of dice, darkness, and decisions.

A virtual tabletop for D&D 5th Edition (SRD 5.2.1).

[Log in]  [GitHub ↗]
```

### Feature grid

Three tiles below the hero. 3-column layout ≥600px, single column on mobile.

| Tile | Heading | Body |
|------|---------|------|
| ⚔ Characters | CHARACTERS | Build your hero. Choose class, background, and origin feat from the full SRD. |
| 🎲 Combat | COMBAT | Fight to survive. Real-time turns, initiative rolls, and full SRD combat rules. |
| 📜 Stories | STORIES | Shape the world. Your master weaves quests while you make choices that matter. |

### Styling

- Tiles: `--bg-surface` background, `--border` border, `--radius` corners, `8px` padding
- Tile heading: `var(--accent)` gold, 11px uppercase, letter-spacing 0.5px
- Tile body: `var(--text-muted)`, 13px, 1.6 line-height
- Grid gap: `12px`

---

## Scope

- Only the **anonymous/logged-out** view gets the feature grid
- Authenticated users keep the existing compact navigation view
- Pure HTML/CSS only — no JS, no backend changes, no new context data
- No new tests required (existing assertions unaffected)

## File to change

- `game/templates/game/index.html` — anonymous section only
