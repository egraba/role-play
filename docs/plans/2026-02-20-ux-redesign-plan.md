# UX Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the rpgui-derived dark-fantasy UI with a clean, flat dark mode — two-column game layout, no gradients/glow animations, system-ui font, minimal components.

**Architecture:** New `rpg-styles.css` replaces the entire existing CSS; templates are restructured for a two-column game layout (game log left, play area right); all embedded `<style>` blocks in partials are removed and consolidated into the main CSS; `game-log.js` is updated to populate a layout-defined container instead of appending a fixed overlay to `document.body`.

**Tech Stack:** Django templates (HTMX), vanilla CSS (no framework), vanilla JS. No Python changes.

**Design doc:** `docs/plans/2026-02-20-ux-redesign-design.md`

---

## Task 1: CSS Design System

**Files:**
- Replace: `game/static/css/rpg-styles.css`

**Step 1: Replace `rpg-styles.css` entirely**

Write the following content to `game/static/css/rpg-styles.css`:

```css
/*
=================================================
Role Play — Design System
=================================================
Clean dark mode. No gradients. No glow. No serif.
=================================================
*/

/* ==================== VARIABLES ==================== */

:root {
  /* New design system */
  --bg:         #111111;
  --bg-surface: #1a1a1a;
  --bg-raised:  #222222;
  --border:     rgba(255, 255, 255, 0.08);
  --text:       #e5e5e5;
  --text-muted: #888888;
  --accent:     #c9a227;
  --red:        #c0392b;
  --green:      #27ae60;
  --blue:       #2980b9;
  --radius:     4px;

  /* Legacy aliases — removed once all inline styles are updated */
  --color-primary:    var(--accent);
  --color-border:     var(--border);
  --color-text:       var(--text);
  --color-text-muted: var(--text-muted);
  --color-health:     var(--red);
  --color-stamina:    var(--green);
  --color-mana:       var(--blue);
  --color-bg-dark:    var(--bg);
  --color-bg-medium:  var(--bg-surface);
  --color-bg-light:   var(--bg-surface);
  --border-radius:    var(--radius);
  --font-text:        system-ui, -apple-system, sans-serif;
  --shadow-default:   none;
  --shadow-glow:      none;
}

/* ==================== RESET ==================== */

*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0;
  padding: 0;
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}

a { color: inherit; }

/* ==================== LAYOUT ==================== */

.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 16px;
}

/* Two-column game layout */
.game-layout {
  display: grid;
  grid-template-columns: 40% 60%;
  height: calc(100vh - 48px);
}

.game-log-col {
  height: 100%;
  overflow: hidden;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
}

.game-play-col {
  height: 100%;
  overflow-y: auto;
}

.play-section {
  padding: 16px;
}

/* ==================== SURFACE ==================== */

.surface {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
}

/* ==================== DIVIDER ==================== */

.divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 0;
}

/* ==================== TYPOGRAPHY ==================== */

h1 { font-size: 20px; font-weight: 600; margin: 0 0 16px; }
h2 { font-size: 16px; font-weight: 600; margin: 0 0 12px; }
h3 { font-size: 14px; font-weight: 600; margin: 0 0 8px; }

.section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.text-muted  { color: var(--text-muted); }
.text-accent { color: var(--accent); }
.text-red    { color: var(--red); }
.text-green  { color: var(--green); }
.text-mono   { font-family: ui-monospace, 'Cascadia Code', monospace; }

.text-center { text-align: center; }
.text-right  { text-align: right; }

/* ==================== BUTTONS ==================== */

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-family: inherit;
  font-size: 13px;
  font-weight: 400;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  cursor: pointer;
  text-decoration: none;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
  white-space: nowrap;
  line-height: 1.4;
  -webkit-appearance: none;
  appearance: none;
}

.btn:hover:not(:disabled):not(.disabled) {
  border-color: rgba(255, 255, 255, 0.2);
}

.btn:disabled, .btn.disabled {
  opacity: 0.35;
  pointer-events: none;
}

.btn-primary {
  border-color: var(--accent);
  color: var(--accent);
}
.btn-primary:hover:not(:disabled) {
  background: rgba(201, 162, 39, 0.08);
}

.btn-ghost {
  border-color: var(--border);
  color: var(--text-muted);
}
.btn-ghost:hover:not(:disabled) {
  color: var(--text);
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-danger {
  border-color: var(--red);
  color: var(--red);
}
.btn-danger:hover:not(:disabled) {
  background: rgba(192, 57, 43, 0.08);
}

/* Legacy button aliases */
.rpg-btn       { display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; font-family: inherit; font-size: 13px; border-radius: var(--radius); border: 1px solid var(--border); background: transparent; color: var(--text); cursor: pointer; text-decoration: none; transition: border-color 0.15s, color 0.15s; white-space: nowrap; -webkit-appearance: none; appearance: none; }
.rpg-btn:hover { border-color: rgba(255,255,255,0.2); }
.btn-attack    { border-color: var(--red);    color: var(--red);    }
.btn-defend    { border-color: var(--border); color: var(--text-muted); }
.btn-skill     { border-color: var(--border); color: var(--text-muted); }

/* ==================== BADGE ==================== */

.badge {
  display: inline-block;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  border-radius: 3px;
  letter-spacing: 0.03em;
}

.badge-green { background: rgba(39, 174, 96, 0.15);   color: var(--green);  }
.badge-red   { background: rgba(192, 57, 43, 0.15);   color: var(--red);    }
.badge-gold  { background: rgba(201, 162, 39, 0.15);  color: var(--accent); }
.badge-muted { background: var(--bg-raised); color: var(--text-muted); }

/* ==================== FORMS ==================== */

input[type="text"],
input[type="number"],
input[type="email"],
input[type="password"],
select,
textarea {
  width: 100%;
  padding: 8px 10px;
  font-family: inherit;
  font-size: 14px;
  background: var(--bg-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  -webkit-appearance: none;
  appearance: none;
}

input[type="text"]:focus,
input[type="number"]:focus,
input[type="email"]:focus,
input[type="password"]:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.2);
}

input::placeholder,
textarea::placeholder { color: var(--text-muted); }

label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.form-group { margin-bottom: 16px; }

/* Legacy form alias */
.rpg-form-group   { margin-bottom: 16px; }
.rpg-select       { width: 100%; padding: 8px 10px; font-family: inherit; font-size: 14px; background: var(--bg-raised); border: 1px solid var(--border); border-radius: var(--radius); color: var(--text); -webkit-appearance: none; appearance: none; }

/* ==================== TABLE ==================== */

.rpg-table {
  width: 100%;
  border-collapse: collapse;
}

.rpg-table th {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.rpg-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}

.rpg-table tr:last-child td { border-bottom: none; }
.rpg-table tr:hover td { background: rgba(255,255,255,0.02); }

/* ==================== NAVBAR ==================== */

.rpg-navbar {
  height: 48px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-container {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 16px;
  gap: 4px;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
  color: var(--text);
  text-decoration: none;
  margin-right: 16px;
}

.navbar-brand img {
  width: 18px;
  height: 18px;
}

.navbar-menu {
  display: flex;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0;
  flex: 1;
}

.navbar-item { display: flex; align-items: center; }

.navbar-link {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 6px 10px;
  font-size: 13px;
  color: var(--text-muted);
  text-decoration: none;
  border-radius: var(--radius);
  transition: color 0.15s;
}

.navbar-link img { display: none; }   /* hide per-link icons */
.navbar-link:hover { color: var(--text); }

.navbar-user { margin-left: auto; position: relative; }

.navbar-user-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  font-family: inherit;
  font-size: 13px;
  color: var(--text-muted);
  background: none;
  border: none;
  cursor: pointer;
  border-radius: var(--radius);
  -webkit-appearance: none;
  appearance: none;
}

.navbar-user-toggle img { display: none; }   /* hide class icon */
.navbar-user-toggle:hover { color: var(--text); }

.navbar-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  min-width: 140px;
  list-style: none;
  padding: 4px 0;
  display: none;
  z-index: 200;
}

.navbar-dropdown.open { display: block; }

.navbar-dropdown-item { display: block; }

.navbar-dropdown-link {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 8px 12px;
  font-size: 13px;
  color: var(--text-muted);
  text-decoration: none;
}

.navbar-dropdown-link img { display: none; }
.navbar-dropdown-link:hover { color: var(--text); background: rgba(255,255,255,0.04); }

/* Mobile toggle */
.navbar-toggle { display: none; }

@media (max-width: 767px) {
  .navbar-toggle {
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 8px;
    margin-left: auto;
    -webkit-appearance: none;
    appearance: none;
  }
  .navbar-toggle-bar {
    width: 20px;
    height: 2px;
    background: var(--text-muted);
    border-radius: 1px;
  }
  .navbar-menu {
    display: none;
    position: absolute;
    top: 48px;
    left: 0;
    right: 0;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    flex-direction: column;
    padding: 8px;
    gap: 2px;
    align-items: stretch;
  }
  .navbar-menu.open { display: flex; }
  .navbar-user { display: none; }
}

/* ==================== MODAL ==================== */

.rpg-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 500;
  padding: 16px;
  display: none;
}

.rpg-modal.active { display: flex; }

.modal-content {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  max-width: 420px;
  width: 100%;
  padding: 20px;
  position: relative;
}

.modal-header {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-header img { display: none; }  /* hide modal header icons */

.modal-close {
  position: absolute;
  top: 12px;
  right: 14px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 18px;
  cursor: pointer;
  line-height: 1;
  padding: 2px 4px;
  -webkit-appearance: none;
  appearance: none;
}

.modal-close:hover { color: var(--text); }

/* ==================== HP BAR ==================== */

.hp-bar {
  height: 8px;
  background: var(--bg-raised);
  border-radius: 4px;
  overflow: hidden;
}

.hp-bar-fill {
  height: 100%;
  background: var(--green);
  transition: width 0.3s ease;
}

.hp-bar-fill.warning  { background: #e67e22; }
.hp-bar-fill.critical { background: var(--red); }

/* ==================== TOGGLE GROUP ==================== */

.toggle-group { display: flex; gap: 4px; }

.toggle-group .btn.active,
.toggle-group .toggle-btn.active {
  border-color: var(--accent);
  color: var(--accent);
}

/* ==================== FLEX UTILITIES ==================== */

.flex         { display: flex; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.flex-end     { display: flex; justify-content: flex-end; align-items: center; }
.gap-4        { gap: 4px; }
.gap-8        { gap: 8px; }
.gap-16       { gap: 16px; }

/* ==================== SPACING UTILITIES ==================== */

.mt-4  { margin-top: 4px; }
.mt-8  { margin-top: 8px; }
.mt-16 { margin-top: 16px; }
.mb-2  { margin-bottom: 8px; }   /* legacy compat */
.mb-4  { margin-bottom: 16px; }  /* legacy compat */
.p-16  { padding: 16px; }

/* ==================== LEGACY CONTAINER ==================== */

/* Used by non-game pages (list, create, etc.) */
.rpg-container { max-width: 960px; margin: 0 auto; padding: 24px 16px; }
.rpg-panel     { background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
.rpg-section   { margin-bottom: 16px; }
.rpg-grid      { display: grid; gap: 16px; }
.rpg-icon      { display: inline-block; vertical-align: middle; }
.rpg-icon-sm   { width: 16px; height: 16px; }
.rpg-icon-md   { width: 20px; height: 20px; }
.rpg-icon-lg   { width: 24px; height: 24px; }
.rpg-icon-xl   { width: 32px; height: 32px; }
.rpg-icon-primary { filter: none; opacity: 0.8; }
.rpg-icon-warning { filter: none; opacity: 0.8; }
.rpg-icon-danger  { filter: none; opacity: 0.8; }
.rpg-icon-success { filter: none; opacity: 0.8; }
.rpg-icon-info    { filter: none; opacity: 0.8; }
.panel-title   { font-size: 16px; font-weight: 600; margin: 0 0 12px; }
.action-buttons { display: flex; flex-wrap: wrap; gap: 8px; }

/* Legacy message classes */
.game-message {
  padding: 12px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg-raised);
}
.game-message.info     { border-color: rgba(41, 128, 185, 0.3); }
.game-message.warning  { border-color: rgba(201, 162, 39, 0.3); }
.game-message.success  { border-color: rgba(39, 174, 96, 0.3);  }
.game-message.danger   { border-color: rgba(192, 57, 43, 0.3);  }

/* ==================== PAGINATION ==================== */

.pagination {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-muted);
  flex-wrap: wrap;
}

.pagination a, .pagination span {
  padding: 4px 8px;
  color: var(--text-muted);
  text-decoration: none;
  border-radius: var(--radius);
}

.pagination a:hover { color: var(--text); }
.pagination .current { color: var(--text); }

/* ==================== MAIN CONTENT ==================== */

.main-content {
  /* No padding — game screen needs full height */
}

/* ==================== SHORTCUTS BUTTON ==================== */

#shortcuts-help-btn {
  position: fixed;
  bottom: 20px;
  left: 20px;
  width: 32px;
  height: 32px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 50%;
  color: var(--text-muted);
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.15s, color 0.15s;
  -webkit-appearance: none;
  appearance: none;
}

#shortcuts-help-btn:hover {
  border-color: rgba(255,255,255,0.2);
  color: var(--text);
}

/* ==================== CONNECTION STATUS ==================== */

#connection-status {
  position: fixed;
  bottom: 20px;
  left: 64px;
  padding: 6px 12px;
  border-radius: var(--radius);
  font-size: 12px;
  z-index: 1000;
  display: none;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--bg-surface);
  color: var(--text-muted);
}

/* ==================== RESPONSIVE ==================== */

@media (max-width: 767px) {
  .game-layout {
    display: block;
    height: auto;
  }
  .game-log-col {
    display: none;
  }
  .game-play-col {
    height: auto;
    overflow-y: visible;
  }
}
```

**Step 2: Run the test suite to confirm no regressions**

```bash
doppler run -- uv run poe test
```

Expected: all tests pass (no Python logic changed).

**Step 3: Start the dev server and do a visual check**

```bash
doppler run -- uv run poe dev-run
```

Navigate to any page. The font should now be system-ui (not Georgia). Background should be `#111`. Gold accent should be `#c9a227`. All existing pages should still render (legacy aliases maintain backward compatibility).

**Step 4: Commit**

```bash
git add game/static/css/rpg-styles.css
git commit -m "style: replace rpg-styles.css with flat dark design system"
```

---

## Task 2: Base Chrome — Navbar

**Files:**
- Modify: `game/templates/base.html`

**Step 1: Update `base.html`**

The navbar currently includes SVG icons on every nav link and the user toggle. The new CSS hides them (`.navbar-link img { display: none }`), so visually they're already gone after Task 1. This step removes the dead markup and cleans up the footer.

Replace the `<footer>` inline styles:

```diff
-<footer style="text-align: center; padding: 20px; margin-top: 40px; border-top: 1px solid var(--color-border, #4a4a4a); font-size: 0.85rem; color: var(--color-text-muted, #999);">
+<footer style="text-align: center; padding: 20px; margin-top: 40px; border-top: 1px solid var(--border); font-size: 12px; color: var(--text-muted);">
```

Remove the per-link SVG images from each `<li>` in the navbar (keep only the brand icon):

```html
<!-- Keep brand icon -->
<a href="{% url 'index' %}" class="navbar-brand">
    <img src="{% static 'images/icons/actions/roll.svg' %}" alt="" class="rpg-icon rpg-icon-primary">
    Role Play
</a>

<!-- Remove icons from these — text only -->
<a href="{% url 'index' %}" class="navbar-link">Home</a>
<a href="{% url 'game-list' %}" class="navbar-link">Games</a>
<a href="{% url 'campaign-list' %}" class="navbar-link">Campaigns</a>
<a href="{{ user_character.get_absolute_url }}" class="navbar-link">My Character</a>
```

For the user dropdown logout link, remove the SVG icon:
```html
<a href="#" class="navbar-dropdown-link" onclick="document.getElementById('logout-form').submit(); return false;">
    Log out
</a>
```

**Step 2: Verify visually and run tests**

```bash
doppler run -- uv run poe test
```

**Step 3: Commit**

```bash
git add game/templates/base.html
git commit -m "style: simplify navbar — remove per-link icons, update footer"
```

---

## Task 3: Game Screen — Two-Column Layout

**Files:**
- Replace: `game/templates/game/game.html`

This is the most significant template change. The floating game log overlay is replaced by an inline left column. All inline styles are removed. DM controls are embedded inline with their relevant sections.

**Step 1: Replace `game/templates/game/game.html`**

```html
{% extends 'base.html' %}
{% load static %}

{% block content %}

<div class="game-layout">

    <!-- ══════════════════════════════════════════ -->
    <!-- LEFT: Game Log                             -->
    <!-- ══════════════════════════════════════════ -->
    <div class="game-log-col" id="game-log-col">
        {% include "game/partials/game_log_panel.html" %}
    </div>

    <!-- ══════════════════════════════════════════ -->
    <!-- RIGHT: Play Area                           -->
    <!-- ══════════════════════════════════════════ -->
    <div class="game-play-col">

        <!-- Quest section -->
        <div class="play-section">
            <div class="flex-between" style="margin-bottom: 8px;">
                <span class="section-label">Quest</span>
                {% if game.master.user == user and flow.is_ongoing %}
                    <a href="{% url 'quest-create' game.id %}" class="btn btn-ghost">Update Quest ▸</a>
                {% endif %}
            </div>
            <div id="quest" style="white-space: pre-line; font-size: 14px; line-height: 1.6;">{{ quest.environment }}</div>
        </div>

        <hr class="divider">

        <!-- Messaging + player actions (ongoing games only) -->
        {% if flow.is_ongoing %}
        <div class="play-section" id="messaging">
            <div style="display: flex; gap: 8px;">
                <input id="message-input" type="text" placeholder="What do you do?" style="flex: 1;">
                <button id="message-submit" class="btn btn-primary" type="button">Send</button>
            </div>
            <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                <button hx-get="{% url 'dice-roller-modal' game.id %}"
                        hx-target="body"
                        hx-swap="beforeend"
                        class="btn btn-ghost"
                        type="button">Roll Dice</button>
                {% if game.master.user == user %}
                    <a href="{% url 'ability-check-request-create' game.id %}" class="btn btn-ghost">Ask for Ability Check</a>
                    <a href="{% url 'combat-create' game.id %}" class="btn btn-ghost">Initiate Combat</a>
                {% endif %}
                {% if player %}
                    {% if ability_check_request %}
                        <button id="ability-check-submit" class="btn btn-primary" type="button">Perform Ability Check</button>
                    {% endif %}
                    {% if saving_throw_request %}
                        <button id="saving-throw-submit" class="btn btn-primary" type="button">Perform Saving Throw</button>
                    {% endif %}
                    {% if combat_initiative_request %}
                        <button id="dexterity-check-submit" class="btn btn-primary" type="button">Roll Initiative</button>
                    {% endif %}
                {% endif %}
            </div>
        </div>
        <hr class="divider">
        {% endif %}

        <!-- Pre-game: DM start button -->
        {% if game.master.user == user and flow.is_under_preparation %}
        <div class="play-section">
            <a href="{% url 'game-start' game.id %}" class="btn btn-primary">Start the Game</a>
        </div>
        <hr class="divider">
        {% endif %}

        <!-- Initiative Tracker (combat only) -->
        {% if combat %}
        <div class="play-section" id="initiative-section">
            <div hx-get="{% url 'initiative-tracker' game.id combat.id %}"
                 hx-trigger="load, initiative-updated from:body"
                 hx-swap="innerHTML">
            </div>
        </div>
        <hr class="divider">

        <!-- Action Panel (combat only) -->
        <div class="play-section" id="action-section">
            <div hx-get="{% url 'action-panel' game.id combat.id %}"
                 hx-trigger="load, initiative-updated from:body, action-taken from:body"
                 hx-swap="innerHTML">
            </div>
        </div>
        <hr class="divider">
        {% endif %}

        <!-- Characters -->
        <div class="play-section">
            <div class="flex-between" style="margin-bottom: 8px;">
                <span class="section-label">Characters</span>
                {% if game.master.user == user %}
                    <a href="{% url 'game-invite-user' game.id %}" class="btn btn-ghost">Invite a User ▸</a>
                {% endif %}
            </div>
            {% for character in character_list %}
                {% with character_user=character.user %}
                    <div style="padding: 4px 0;">
                        <a href="{{ character.get_absolute_url }}" style="color: var(--accent);">{{ character }}</a>
                        <span class="text-muted">
                            {% if character_user == user %}(you){% else %}({{ character_user }}){% endif %}
                        </span>
                    </div>
                {% endwith %}
            {% empty %}
                <p class="text-muted">No characters in this game yet.</p>
            {% endfor %}
        </div>

    </div><!-- /.game-play-col -->
</div><!-- /.game-layout -->

{% include "game/partials/keyboard_shortcuts_modal.html" %}
{% include "game/partials/quick_reference_panels.html" %}

<button id="shortcuts-help-btn"
        onclick="window.keyboardShortcuts && window.keyboardShortcuts.toggleHelp(event)"
        title="Keyboard shortcuts (?)">?</button>

<script>
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const url = wsProtocol + window.location.host + '/events/' + {{ game.id }} + '/';

    const input = document.getElementById('message-input');
    const sendButton = document.getElementById('message-submit');
    const abilityCheckButton = document.getElementById('ability-check-submit');
    const dexterityCheckButton = document.getElementById('dexterity-check-submit');
    const savingThrowButton = document.getElementById('saving-throw-submit');

    const MESSAGE = "message";
    const QUEST_UPDATE = "quest.update";
    const ABILITY_CHECK_RESPONSE = "ability.check.response";
    const SAVING_THROW_RESPONSE = "saving.throw.response";
    const COMBAT_INITIATIVE_RESPONSE = "combat.initiative.response";
    const DICE_ROLL = "dice.roll";

    let eventsSocket = null;
    let reconnectAttempts = 0;
    const baseReconnectDelay = 1000;
    const maxReconnectDelay = 30000;
    let reconnectTimeout = null;

    const connectionStatus = (function() {
        const el = document.createElement('div');
        el.id = 'connection-status';
        el.title = 'Click to retry connection';
        el.addEventListener('click', function() {
            clearTimeout(reconnectTimeout);
            reconnectAttempts = 0;
            el.textContent = 'Reconnecting...';
            el.style.display = 'block';
            connectWebSocket();
        });
        document.body.appendChild(el);
        return el;
    })();

    function showConnectionStatus(message) {
        connectionStatus.textContent = message;
        connectionStatus.style.display = 'block';
    }

    function hideConnectionStatus() {
        connectionStatus.style.display = 'none';
    }

    function connectWebSocket() {
        if (eventsSocket && eventsSocket.readyState === WebSocket.OPEN) return;
        eventsSocket = new WebSocket(url);

        eventsSocket.onopen = function() {
            reconnectAttempts = 0;
            hideConnectionStatus();
            if (input) input.disabled = false;
            if (sendButton) sendButton.disabled = false;
        };

        eventsSocket.onmessage = function(event) {
            const message = JSON.parse(event.data);
            if (window.gameLog) window.gameLog.handleWebSocketEvent(message);

            if (message["type"] === QUEST_UPDATE) {
                htmx.ajax('GET', window.location.pathname, {target: '#quest', swap: 'innerHTML'});
            } else if (message["type"] === MESSAGE || message["type"] === DICE_ROLL) {
                // handled by game log
            } else if (
                message["type"].startsWith("turn.") ||
                message["type"].startsWith("combat.") ||
                message["type"].startsWith("hp.") ||
                message["type"].startsWith("concentration.") ||
                message["type"] === "action.taken"
            ) {
                htmx.trigger(document.body, 'initiative-updated');
            } else {
                location.reload();
            }
        };

        eventsSocket.onclose = function() { scheduleReconnect(); };
        eventsSocket.onerror = function() {};
    }

    function scheduleReconnect() {
        clearTimeout(reconnectTimeout);
        if (input) input.disabled = true;
        if (sendButton) sendButton.disabled = true;
        const delay = Math.min(
            baseReconnectDelay * Math.pow(2, reconnectAttempts) + Math.random() * 1000,
            maxReconnectDelay
        );
        reconnectAttempts++;
        showConnectionStatus('Reconnecting... (attempt ' + reconnectAttempts + ')');
        reconnectTimeout = setTimeout(connectWebSocket, delay);
    }

    function sendMessage(data) {
        if (eventsSocket && eventsSocket.readyState === WebSocket.OPEN) {
            eventsSocket.send(JSON.stringify(data));
            return true;
        }
        showConnectionStatus('Not connected. Reconnecting...');
        scheduleReconnect();
        return false;
    }

    connectWebSocket();

    if (sendButton) {
        sendButton.addEventListener('click', function() {
            const userInput = input.value.trim();
            if (userInput && sendMessage({'type': MESSAGE, 'date': Date.now(), 'username': '{{ user.username }}', 'message': userInput})) {
                input.value = '';
                input.focus();
            }
        });
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') { e.preventDefault(); sendButton.click(); }
        });
    }

    if (abilityCheckButton) {
        abilityCheckButton.addEventListener('click', function() {
            sendMessage({'type': ABILITY_CHECK_RESPONSE, 'date': Date.now(), 'username': '{{ user.username }}'});
        });
    }

    if (savingThrowButton) {
        savingThrowButton.addEventListener('click', function() {
            sendMessage({'type': SAVING_THROW_RESPONSE, 'date': Date.now(), 'username': '{{ user.username }}'});
        });
    }

    if (dexterityCheckButton) {
        dexterityCheckButton.addEventListener('click', function() {
            sendMessage({'type': COMBAT_INITIATIVE_RESPONSE, 'date': Date.now(), 'username': '{{ user.username }}'});
        });
    }

    if (input) input.focus();

    // Modal close handlers (unchanged logic, cleaner)
    document.body.addEventListener('attack-modal-closed', function() {
        document.querySelectorAll('#attack-modal').forEach(m => m.remove());
        htmx.trigger(document.body, 'action-taken');
    });
    document.body.addEventListener('damage-applied', function() {
        document.querySelectorAll('#attack-modal').forEach(m => m.remove());
        htmx.trigger(document.body, 'initiative-updated');
    });
    document.body.addEventListener('dice-roller-closed', function() {
        document.querySelectorAll('#dice-roller-modal').forEach(m => m.remove());
    });
    document.body.addEventListener('concentration-modal-closed', function() {
        document.querySelectorAll('#concentration-save-modal').forEach(m => m.remove());
        htmx.trigger(document.body, 'initiative-updated');
    });

    document.addEventListener('click', function(e) {
        const modal = e.target;
        if (modal.classList && modal.classList.contains('rpg-modal') && modal.classList.contains('active')) {
            modal.classList.remove('active');
            const id = modal.id;
            if (id === 'attack-modal') htmx.trigger(document.body, 'attack-modal-closed');
            if (id === 'dice-roller-modal') htmx.trigger(document.body, 'dice-roller-closed');
            if (id === 'concentration-save-modal') htmx.trigger(document.body, 'concentration-modal-closed');
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key !== 'Escape') return;
        ['attack-modal', 'dice-roller-modal', 'concentration-save-modal'].forEach(function(id) {
            const m = document.getElementById(id);
            if (m && m.classList.contains('active')) {
                m.classList.remove('active');
                const events = {
                    'attack-modal': 'attack-modal-closed',
                    'dice-roller-modal': 'dice-roller-closed',
                    'concentration-save-modal': 'concentration-modal-closed'
                };
                htmx.trigger(document.body, events[id]);
            }
        });
    });
</script>

<script src="{% static 'js/keyboard-shortcuts.js' %}"></script>

{% endblock %}
```

**Step 2: Run tests and verify visually**

```bash
doppler run -- uv run poe test
```

Navigate to an active game. Verify:
- Two-column layout appears
- Quest text displays in right column
- Message input works
- Combat sections appear when in combat

**Step 3: Commit**

```bash
git add game/templates/game/game.html
git commit -m "refactor: game screen two-column layout, remove floating log overlay"
```

---

## Task 4: Game Log — Left Column

**Files:**
- Modify: `game/templates/game/partials/game_log_panel.html`
- Replace: `game/static/css/game-log.css`
- Modify: `game/static/js/game-log.js`

The game log JS currently creates a fixed-position panel and appends it to `document.body`. In the new layout, it populates `#game-log-col` which is already in the template. Update the JS constructor to accept a container ID.

**Step 1: Update `game_log_panel.html`**

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/game-log.css' %}">
<script src="{% static 'js/game-log.js' %}"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        window.gameLog = new GameLog({{ game.id }}, '{{ user.username }}', 'game-log-col');
    });
</script>
```

**Step 2: Update `game-log.js` — `createPanel()` method**

Find the `createPanel()` method. Change it to populate the provided container instead of appending to `body`. The outer panel div and expand button are no longer needed — the column IS the panel.

Find:
```javascript
createPanel() {
    var panel = document.createElement("div");
    panel.className = "game-log-panel";
    panel.id = "game-log-panel";
```

The `createPanel()` method should now build the log header, filter bar, and entries stream directly inside the container element:

```javascript
createPanel() {
    var container = document.getElementById(this.containerId);
    if (!container) return;

    var header = this._createHeader();
    var entries = document.createElement("div");
    entries.className = "game-log-stream";
    entries.id = "game-log-entries";

    var indicator = document.createElement("div");
    indicator.className = "new-events-indicator";
    indicator.id = "new-events-indicator";
    indicator.appendChild(document.createTextNode("↓ "));
    var countSpan = document.createElement("span");
    countSpan.id = "new-events-count";
    countSpan.textContent = "0";
    indicator.appendChild(countSpan);
    indicator.appendChild(document.createTextNode(" new"));

    var filters = this._createFilters();

    container.appendChild(header);
    container.appendChild(entries);
    container.appendChild(indicator);
    container.appendChild(filters);

    // No expand button needed — column is always visible
    this.panel = container;
    this.entriesContainer = entries;
    this.newEventsIndicator = indicator;
    this.newEventsCountEl = countSpan;
    this.expandBtn = null;
}
```

Also update the constructor to accept `containerId`:
```javascript
constructor(gameId, username, containerId) {
    this.gameId = gameId;
    this.username = username;
    this.containerId = containerId || 'game-log-col';
    // ... rest unchanged
```

Remove any method calls that reference `this.expandBtn` by guarding them: `if (this.expandBtn) { ... }`.

Remove the `toggleCollapse()` method or guard it similarly — the column is always visible.

**Step 3: Replace `game-log.css`**

```css
/* ==================== GAME LOG COLUMN ==================== */

/* The column shell is styled in rpg-styles.css (.game-log-col) */

.game-log-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.game-log-header h3 {
    margin: 0;
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
}

.game-log-toggle {
    display: none;  /* collapse not needed in column layout */
}

/* ==================== EVENT STREAM ==================== */

.game-log-stream {
    flex: 1;
    overflow-y: auto;
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.event-entry {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.event-meta {
    display: flex;
    align-items: center;
    gap: 8px;
}

.event-sender {
    font-size: 12px;
    font-weight: 600;
    color: var(--text);
}

.event-sender.system {
    color: var(--text-muted);
}

.event-type-icon {
    font-size: 10px;
    color: var(--text-muted);
}

.event-time {
    font-size: 11px;
    color: var(--text-muted);
    margin-left: auto;
}

.event-content {
    font-size: 13px;
    color: var(--text);
    line-height: 1.5;
    padding-left: 0;
}

/* Category-specific content colors */
.event-entry.category-combat .event-content  { color: var(--text); }
.event-entry.category-rolls .event-content   { color: var(--text); }
.event-entry.category-dm .event-content      { color: var(--text-muted); font-style: italic; }

/* ==================== NEW EVENTS INDICATOR ==================== */

.new-events-indicator {
    display: none;
    text-align: center;
    padding: 6px;
    font-size: 12px;
    color: var(--accent);
    cursor: pointer;
    background: var(--bg-surface);
    border-top: 1px solid var(--border);
    flex-shrink: 0;
}

.new-events-indicator.visible { display: block; }

/* ==================== FILTER BAR ==================== */

.game-log-filters {
    padding: 0 4px;
    border-top: 1px solid var(--border);
    display: flex;
    flex-shrink: 0;
    overflow-x: auto;
}

.filter-toggles {
    display: flex;
    gap: 0;
}

.filter-toggle {
    padding: 8px 10px;
    font-size: 12px;
    font-family: inherit;
    color: var(--text-muted);
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: color 0.15s;
    white-space: nowrap;
    -webkit-appearance: none;
    appearance: none;
}

.filter-toggle:hover { color: var(--text); }

.filter-toggle.active {
    color: var(--text);
    border-bottom-color: var(--accent);
}

/* ==================== SEARCH BAR ==================== */

.game-log-search { display: none; }  /* removed per design */

/* ==================== LEGACY COMPAT ==================== */

/* The old panel class — kept so JS doesn't break while being updated */
.game-log-panel { display: contents; }
.game-log-entries { flex: 1; overflow-y: auto; padding: 12px 16px; }
.game-log-expand-btn { display: none; }

/* ==================== RESPONSIVE ==================== */

@media (max-width: 767px) {
    .game-log-filters {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--bg-surface);
        border-top: 1px solid var(--border);
        justify-content: center;
        z-index: 50;
    }
}
```

**Step 4: Run tests and verify**

```bash
doppler run -- uv run poe test
```

Check the game log column renders in the left column, events appear, filter tabs work.

**Step 5: Commit**

```bash
git add game/templates/game/partials/game_log_panel.html \
        game/static/css/game-log.css \
        game/static/js/game-log.js
git commit -m "style: game log — inline column layout, remove fixed overlay"
```

---

## Task 5: Initiative Tracker

**Files:**
- Replace: `game/templates/game/partials/initiative_tracker.html`

Remove the embedded `<style>` block (1 of 4 large partial style blocks). Move DM controls to the section header. Remove pulse animations — the current turn is indicated by accent color only.

**Step 1: Replace `initiative_tracker.html`**

```html
<div id="initiative-tracker">

    <div class="flex-between" style="margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span class="section-label">Initiative</span>
            <span class="text-muted" style="font-size: 12px;">Round {{ current_round }}</span>
        </div>
        {% if is_dm %}
        <div style="display: flex; gap: 8px;">
            <form action="{% url 'combat-advance-turn' game.id combat.id %}" method="post" style="display: inline;">
                {% csrf_token %}
                <button type="submit" class="btn btn-ghost" style="font-size: 12px;">Next Turn</button>
            </form>
            <form action="{% url 'combat-end' game.id combat.id %}" method="post" style="display: inline;">
                {% csrf_token %}
                <button type="submit" class="btn btn-danger" style="font-size: 12px;">End Combat</button>
            </form>
        </div>
        {% endif %}
    </div>

    <div style="display: flex; flex-direction: column; gap: 4px;">
        {% for data in fighters %}
        <div style="display: grid; grid-template-columns: 32px 1fr auto; gap: 10px; align-items: center; padding: 8px; border-radius: var(--radius); background: {% if data.is_current %}rgba(201, 162, 39, 0.06){% else %}transparent{% endif %};">

            <!-- Initiative value -->
            <span class="text-mono" style="font-size: 13px; text-align: center; color: {% if data.is_current %}var(--accent){% else %}var(--text-muted){% endif %};">
                {{ data.initiative|default:"—" }}
            </span>

            <!-- Name + HP -->
            <div>
                <div style="font-size: 13px; font-weight: {% if data.is_current %}600{% else %}400{% endif %}; color: {% if data.is_current %}var(--accent){% else %}var(--text){% endif %};">
                    {{ data.character.name }}
                    {% if data.is_owned_by_user %}<span class="text-muted" style="font-weight: 400;"> (you)</span>{% endif %}
                    {% if data.is_surprised %}<span class="badge badge-muted" style="margin-left: 4px;">surprised</span>{% endif %}
                </div>
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 3px;">
                    <div class="hp-bar" style="flex: 1; max-width: 100px;">
                        <div class="hp-bar-fill {% if data.hp_percentage <= 25 %}critical{% elif data.hp_percentage <= 50 %}warning{% endif %}"
                             style="width: {{ data.hp_percentage }}%;"></div>
                    </div>
                    <span style="font-size: 11px; color: var(--text-muted);">{{ data.hp }}/{{ data.max_hp }}</span>
                    {% if data.concentration %}
                        <span class="badge badge-muted" title="Concentrating on {{ data.concentration.spell.name }}">conc.</span>
                    {% endif %}
                    {% for char_condition in data.conditions %}
                        <span class="badge badge-red" style="font-size: 10px;" title="{{ char_condition.condition }}{% if char_condition.exhaustion_level %} L{{ char_condition.exhaustion_level }}{% endif %}">{{ char_condition.condition.name|lower }}</span>
                    {% endfor %}
                </div>
            </div>

            <!-- Turn actions -->
            <div style="display: flex; gap: 4px;">
                {% if data.is_player_turn %}
                    <button hx-post="{% url 'combat-ready' game.id combat.id %}"
                            hx-target="#initiative-tracker"
                            hx-swap="outerHTML"
                            class="btn btn-ghost" style="font-size: 11px; padding: 3px 8px;">Ready</button>
                    <button hx-post="{% url 'combat-delay' game.id combat.id %}"
                            hx-target="#initiative-tracker"
                            hx-swap="outerHTML"
                            class="btn btn-ghost" style="font-size: 11px; padding: 3px 8px;">Delay</button>
                {% elif data.is_current %}
                    <span style="width: 8px; height: 8px; background: var(--accent); border-radius: 50%; display: inline-block; margin: auto;"></span>
                {% endif %}
            </div>

        </div>
        {% empty %}
            <p class="text-muted">No combatants in initiative order.</p>
        {% endfor %}
    </div>

</div>
```

**Step 2: Run tests and verify**

```bash
doppler run -- uv run poe test
```

**Step 3: Commit**

```bash
git add game/templates/game/partials/initiative_tracker.html
git commit -m "style: initiative tracker — remove embedded styles and animations"
```

---

## Task 6: Action Panel

**Files:**
- Replace: `game/templates/game/partials/action_panel.html`

Remove the embedded `<style>` block (~460 lines). Change the 2×2 grid layout to four plain rows.

**Step 1: Replace `action_panel.html`**

```html
<div id="action-panel" {% if not is_player_turn %}style="opacity: 0.5; pointer-events: none;"{% endif %}>

    <div class="flex-between" style="margin-bottom: 12px;">
        <span class="section-label">Actions</span>
        {% if is_player_turn %}<span class="badge badge-green">Your Turn</span>{% endif %}
    </div>

    {% if concentration %}
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; border: 1px solid rgba(155, 89, 182, 0.3); border-radius: var(--radius); margin-bottom: 12px; font-size: 12px;">
        <span class="text-muted">Concentrating: <span style="color: var(--text);">{{ concentration.spell.name }}</span></span>
        {% if can_break_concentration %}
            <button type="button"
                    class="btn btn-ghost" style="font-size: 11px; padding: 3px 8px;"
                    hx-post="{% url 'character-break-concentration' concentration.character.pk %}"
                    hx-target="#action-panel"
                    hx-swap="outerHTML">Drop</button>
        {% endif %}
    </div>
    {% endif %}

    <!-- Action row -->
    <div style="display: flex; align-items: flex-start; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--border);">
        <span style="font-size: 12px; color: var(--text-muted); width: 80px; flex-shrink: 0; padding-top: 7px;">
            Action {% if turn.action_used %}<span class="text-muted" style="text-decoration: line-through; font-size: 10px;">used</span>{% endif %}
        </span>
        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            {% for action in standard_actions %}
                {% if action.value == 'attack' %}
                    <button class="btn {% if turn.action_used %}disabled btn-ghost{% else %}btn-ghost{% endif %}"
                            {% if not turn.action_used and is_player_turn %}
                                hx-get="{% url 'combat-attack-modal' game.id combat.id %}"
                                hx-target="body"
                                hx-swap="beforeend"
                            {% else %}
                                disabled
                            {% endif %}>{{ action.label }}</button>
                {% else %}
                    <button class="btn {% if turn.action_used %}disabled btn-ghost{% else %}btn-ghost{% endif %}"
                            {% if not turn.action_used and is_player_turn %}
                                hx-post="{% url 'combat-take-action' game.id combat.id %}"
                                hx-vals='{"action": "{{ action.value }}", "action_type": "A"}'
                                hx-target="#action-panel"
                                hx-swap="outerHTML"
                            {% else %}
                                disabled
                            {% endif %}>{{ action.label }}</button>
                {% endif %}
            {% endfor %}
        </div>
    </div>

    <!-- Bonus action row -->
    <div style="display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--border);">
        <span style="font-size: 12px; color: var(--text-muted); width: 80px; flex-shrink: 0;">Bonus</span>
        <span style="font-size: 12px; color: {% if turn.bonus_action_used %}var(--text-muted){% else %}var(--text){% endif %};">
            {% if turn.bonus_action_used %}spent{% else %}available{% endif %}
        </span>
    </div>

    <!-- Reaction row -->
    <div style="display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--border);">
        <span style="font-size: 12px; color: var(--text-muted); width: 80px; flex-shrink: 0;">Reaction</span>
        <span style="font-size: 12px; color: {% if turn.reaction_used %}var(--text-muted){% else %}var(--text){% endif %};">
            {% if turn.reaction_used %}spent{% else %}available{% endif %}
        </span>
    </div>

    <!-- Movement row -->
    <div style="display: flex; align-items: center; gap: 8px; padding: 8px 0;">
        <span style="font-size: 12px; color: var(--text-muted); width: 80px; flex-shrink: 0;">Movement</span>
        <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <div class="hp-bar" style="flex: 1; max-width: 120px;">
                    <div class="hp-bar-fill" style="background: var(--blue); width: {% widthratio turn.remaining_movement turn.movement_total 100 %}%;"></div>
                </div>
                <span style="font-size: 12px; color: var(--text-muted);">{{ turn.remaining_movement }}/{{ turn.movement_total }} ft</span>
            </div>
            {% if is_player_turn and turn.remaining_movement > 0 %}
            <div style="display: flex; gap: 4px;">
                <button class="btn btn-ghost" style="font-size: 11px; padding: 3px 8px;"
                        hx-post="{% url 'combat-move' game.id combat.id %}"
                        hx-vals='{"feet": "5"}'
                        hx-target="#action-panel"
                        hx-swap="outerHTML">5 ft</button>
                <button class="btn btn-ghost" style="font-size: 11px; padding: 3px 8px;"
                        hx-post="{% url 'combat-move' game.id combat.id %}"
                        hx-vals='{"feet": "10"}'
                        hx-target="#action-panel"
                        hx-swap="outerHTML">10 ft</button>
                <button class="btn btn-ghost" style="font-size: 11px; padding: 3px 8px;"
                        hx-post="{% url 'combat-move' game.id combat.id %}"
                        hx-vals='{"feet": "{{ turn.remaining_movement }}"}'
                        hx-target="#action-panel"
                        hx-swap="outerHTML">All</button>
            </div>
            {% endif %}
        </div>
    </div>

    {% if actions_taken %}
    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
        <span class="section-label" style="display: block; margin-bottom: 8px;">Actions Taken</span>
        {% for action in actions_taken %}
        <div style="font-size: 12px; color: var(--text-muted); padding: 3px 0;">
            <span class="badge badge-muted" style="font-size: 10px;">{{ action.get_action_type_display }}</span>
            {{ action.get_action_display }}
            {% if action.target_fighter %} → {{ action.target_fighter }}{% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

</div>
```

**Step 2: Run tests and verify**

```bash
doppler run -- uv run poe test
```

**Step 3: Commit**

```bash
git add game/templates/game/partials/action_panel.html
git commit -m "style: action panel — four-row layout, remove embedded styles"
```

---

## Task 7: Attack Modal

**Files:**
- Replace: `game/templates/game/partials/attack_modal.html`

Remove the embedded `<style>` block (~530 lines of animations and fantasy chrome). Replace the d20 animation die with a large plain monospace number. Keep the 3-step HTMX flow intact.

**Step 1: Replace `attack_modal.html`**

```html
{% load static %}

<div id="attack-modal" class="rpg-modal {% if show_modal %}active{% endif %}">
    <div class="modal-content">
        <button class="modal-close" onclick="closeAttackModal()" type="button">&times;</button>

        {% if not attack_result %}
        <!-- Step 1: Setup -->
        <div class="modal-header">Attack</div>
        <form id="attack-form"
              hx-post="{% url 'combat-attack-roll' game.id combat.id %}"
              hx-target="#attack-modal"
              hx-swap="outerHTML">

            <div class="form-group">
                <label>Target</label>
                <select name="target_id" class="rpg-select" required>
                    <option value="">— choose a target —</option>
                    {% for fighter in targets %}
                        <option value="{{ fighter.id }}" {% if selected_target == fighter.id %}selected{% endif %}>
                            {{ fighter.character.name }} (AC {{ fighter.character.ac|default:"10" }})
                        </option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label>Weapon</label>
                <select name="weapon_id" class="rpg-select" required>
                    {% for wd in weapons %}
                        <option value="{{ wd.weapon.id }}"
                                data-attack-bonus="{{ wd.attack_bonus }}"
                                data-damage="{{ wd.damage }}">
                            {{ wd.weapon.settings.name }} ({{ wd.damage }}, +{{ wd.attack_bonus }})
                        </option>
                    {% empty %}
                        <option value="">— no weapons equipped —</option>
                    {% endfor %}
                </select>
            </div>

            <div class="form-group">
                <label>Modifier</label>
                <div class="toggle-group">
                    <button type="button" class="btn btn-ghost {% if roll_modifier == 'disadvantage' %}active{% endif %}"
                            data-value="disadvantage" onclick="setRollModifier(this, 'disadvantage')">Disadvantage</button>
                    <button type="button" class="btn btn-ghost {% if roll_modifier == 'normal' or not roll_modifier %}active{% endif %}"
                            data-value="normal" onclick="setRollModifier(this, 'normal')">Normal</button>
                    <button type="button" class="btn btn-ghost {% if roll_modifier == 'advantage' %}active{% endif %}"
                            data-value="advantage" onclick="setRollModifier(this, 'advantage')">Advantage</button>
                </div>
                <input type="hidden" name="roll_modifier" id="roll-modifier-input" value="{{ roll_modifier|default:'normal' }}">
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; margin-bottom: 4px;">
                <span class="text-muted" style="font-size: 12px;">Attack bonus</span>
                <span style="font-size: 16px; font-weight: 600; color: var(--accent);">+{{ attack_bonus|default:"0" }}</span>
            </div>

            <div class="flex-end gap-8" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border);">
                <button type="button" class="btn btn-ghost" onclick="closeAttackModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Roll Attack</button>
            </div>
        </form>

        {% else %}
        <!-- Step 2: Attack result -->
        <div class="modal-header">
            Attack vs {{ target.character.name }} (AC {{ target.character.ac|default:"10" }})
        </div>

        <div style="text-align: center; padding: 16px 0;">
            <div class="text-mono" style="font-size: 48px; font-weight: 700; color: var(--accent); line-height: 1;">
                {{ natural_roll }}
            </div>
            {% if roll_modifier != 'normal' %}
            <div class="text-muted" style="font-size: 12px; margin-top: 4px;">
                ({{ second_roll }}) — {% if roll_modifier == 'advantage' %}Advantage{% else %}Disadvantage{% endif %}
            </div>
            {% endif %}
            <div class="text-muted" style="font-size: 13px; margin-top: 8px;">
                {{ natural_roll }} + {{ attack_bonus }} = <strong style="color: var(--text);">{{ total_roll }}</strong>
            </div>
            <div style="margin-top: 12px;">
                {% if is_critical_hit %}
                    <span class="badge badge-green" style="font-size: 14px; padding: 4px 12px;">Critical Hit!</span>
                {% elif is_critical_miss %}
                    <span class="badge badge-red" style="font-size: 14px; padding: 4px 12px;">Critical Miss</span>
                {% elif is_hit %}
                    <span class="badge badge-green" style="font-size: 14px; padding: 4px 12px;">Hit</span>
                {% else %}
                    <span class="badge badge-red" style="font-size: 14px; padding: 4px 12px;">Miss</span>
                {% endif %}
            </div>
            {% if weapon_name %}
            <div class="text-muted" style="font-size: 12px; margin-top: 8px;">{{ weapon_name }}</div>
            {% endif %}
        </div>

        {% if is_hit %}
        <div style="border-top: 1px solid var(--border); padding-top: 12px; margin-top: 4px;">
            {% if damage_rolled %}
            <!-- Damage result -->
            <div style="text-align: center; padding: 8px 0;">
                <div class="text-muted" style="font-size: 12px;">{{ damage_formula }}</div>
                <div class="text-mono" style="font-size: 32px; font-weight: 700; color: var(--red); line-height: 1.2; margin-top: 4px;">
                    {{ total_damage }}
                    <span style="font-size: 14px; font-weight: 400; color: var(--text-muted);">damage</span>
                </div>
            </div>
            <form hx-post="{% url 'combat-apply-damage' game.id combat.id %}"
                  hx-target="#attack-modal"
                  hx-swap="outerHTML">
                <input type="hidden" name="target_id" value="{{ target.id }}">
                <input type="hidden" name="weapon_id" value="{{ weapon_id }}">
                <input type="hidden" name="damage" value="{{ total_damage }}">
                <div class="flex-end gap-8">
                    <button type="button" class="btn btn-ghost" onclick="closeAttackModal()">Cancel</button>
                    <button type="submit" class="btn btn-danger">Apply {{ total_damage }} Damage</button>
                </div>
            </form>

            {% else %}
            <!-- Roll damage -->
            <form hx-post="{% url 'combat-damage-roll' game.id combat.id %}"
                  hx-target="#attack-modal"
                  hx-swap="outerHTML">
                <input type="hidden" name="target_id" value="{{ target.id }}">
                <input type="hidden" name="weapon_id" value="{{ weapon_id }}">
                <input type="hidden" name="is_critical" value="{{ is_critical_hit|yesno:'true,false' }}">
                <input type="hidden" name="natural_roll" value="{{ natural_roll }}">
                <input type="hidden" name="total_roll" value="{{ total_roll }}">
                <input type="hidden" name="attack_bonus" value="{{ attack_bonus }}">
                <input type="hidden" name="total_damage" value="{{ total_damage }}">
                <input type="hidden" name="damage_rolls" value="{{ damage_rolls|join:',' }}">
                <input type="hidden" name="damage_formula" value="{{ damage_formula }}">
                <div class="flex-end gap-8">
                    <button type="button" class="btn btn-ghost" onclick="closeAttackModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Roll Damage</button>
                </div>
            </form>
            {% endif %}
        </div>

        {% else %}
        <!-- Miss -->
        <div class="flex-end" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border);">
            <button type="button" class="btn btn-ghost" onclick="closeAttackModal()">Close</button>
        </div>
        {% endif %}
        {% endif %}

        {% if damage_applied %}
        <!-- Step 3: Damage applied -->
        <div style="text-align: center; padding: 8px 0;">
            <div style="font-size: 15px; font-weight: 600; color: var(--green); margin-bottom: 8px;">Damage Applied</div>
            <div style="font-size: 13px; color: var(--text);">
                {{ target.character.name }} took {{ damage_applied }} damage
            </div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
                HP: {{ target.character.hp }} / {{ target.character.max_hp }}
            </div>
        </div>

        {% if concentration_info %}
        <div style="padding: 12px; border: 1px solid rgba(155, 89, 182, 0.3); border-radius: var(--radius); margin-top: 12px; font-size: 13px;">
            <div style="font-weight: 600; color: var(--text); margin-bottom: 4px;">Concentration check required</div>
            <div class="text-muted">
                {{ target.character.name }} must make a DC {{ concentration_info.dc }}
                Constitution save to maintain {{ concentration_info.spell_name }}.
            </div>
        </div>
        <div class="flex-end gap-8" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border);">
            <button type="button" class="btn btn-ghost" onclick="closeAttackModal()">Later</button>
            <button type="button"
                    class="btn btn-primary"
                    hx-get="{% url 'concentration-save-modal' game.id concentration_info.character_id %}?damage={{ concentration_info.damage }}"
                    hx-target="body"
                    hx-swap="beforeend"
                    onclick="closeAttackModal()">Roll Concentration Save</button>
        </div>
        {% else %}
        <div class="flex-end" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border);">
            <button type="button" class="btn btn-ghost" onclick="closeAttackModal()">Close</button>
        </div>
        {% endif %}
        {% endif %}

    </div>
</div>

<script>
    function setRollModifier(button, value) {
        document.querySelectorAll('.toggle-group .btn').forEach(b => b.classList.remove('active'));
        button.classList.add('active');
        document.getElementById('roll-modifier-input').value = value;
    }

    function closeAttackModal() {
        const modal = document.getElementById('attack-modal');
        if (modal) modal.classList.remove('active');
        htmx.trigger(document.body, 'attack-modal-closed');
    }
</script>
```

**Step 2: Run tests and verify**

```bash
doppler run -- uv run poe test
```

Verify the 3-step attack flow: setup → roll result shows large number with HIT/MISS badge → damage roll → apply damage confirmation.

**Step 3: Commit**

```bash
git add game/templates/game/partials/attack_modal.html
git commit -m "style: attack modal — remove animations and embedded styles"
```

---

## Task 8: Dice Roller and Concentration Save Modals

**Files:**
- Replace: `game/templates/game/partials/dice_roller_modal.html`
- Replace: `game/templates/game/partials/concentration_save_modal.html`

**Step 1: Replace `dice_roller_modal.html`**

```html
{% load static %}

<div id="dice-roller-modal" class="rpg-modal {% if show_modal %}active{% endif %}">
    <div class="modal-content">
        <button class="modal-close" onclick="closeDiceRollerModal()" type="button">&times;</button>
        <div class="modal-header">Roll Dice</div>

        {% if error %}
        <div style="padding: 8px 12px; border: 1px solid rgba(192,57,43,0.4); border-radius: var(--radius); color: var(--red); font-size: 13px; margin-bottom: 12px;">
            {{ error }}
        </div>
        {% endif %}

        {% if not roll_result %}
        <form id="dice-roller-form"
              hx-post="{% url 'dice-roll' game.id %}"
              hx-target="#dice-roller-modal"
              hx-swap="outerHTML">

            <div class="form-group">
                <label>Die type</label>
                <div class="toggle-group" style="flex-wrap: wrap;">
                    {% for die in dice_types %}
                        <button type="button"
                                class="btn btn-ghost {% if die.value == 20 %}active{% endif %}"
                                data-value="{{ die.value }}"
                                onclick="selectDiceType(this, {{ die.value }})">{{ die.label }}</button>
                    {% endfor %}
                </div>
                <input type="hidden" name="dice_type" id="dice-type-input" value="20">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div class="form-group">
                    <label>Count</label>
                    <input type="number" name="num_dice" id="num-dice-input" value="1" min="1" max="10">
                </div>
                <div class="form-group">
                    <label>Modifier</label>
                    <input type="number" name="modifier" id="modifier-input" value="0" min="-20" max="20">
                </div>
            </div>

            <div class="form-group">
                <label>Purpose (optional)</label>
                <input type="text" name="roll_purpose" id="roll-purpose-input"
                       placeholder="e.g. Perception check" maxlength="50">
            </div>

            <div style="text-align: center; padding: 8px; font-size: 18px; font-weight: 600;
                        color: var(--accent); font-family: ui-monospace, monospace;" id="roll-preview-display">
                1d20
            </div>

            <div class="flex-end gap-8" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border);">
                <button type="button" class="btn btn-ghost" onclick="closeDiceRollerModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Roll</button>
            </div>
        </form>

        {% else %}
        <div style="text-align: center; padding: 8px 0;">
            {% if roll_purpose %}
            <div class="text-muted" style="font-size: 12px; margin-bottom: 12px;">{{ roll_purpose }}</div>
            {% endif %}

            <div class="text-mono" style="font-size: 13px; color: var(--text-muted); margin-bottom: 4px;">
                {{ dice_notation }}{% if modifier > 0 %} +{{ modifier }}{% elif modifier < 0 %} {{ modifier }}{% endif %}
                =
                ({% for roll in individual_rolls %}{{ roll }}{% if not forloop.last %} + {% endif %}{% endfor %}){% if modifier != 0 %} {% if modifier > 0 %}+{% endif %}{{ modifier }}{% endif %}
            </div>

            <div class="text-mono" style="font-size: 48px; font-weight: 700; color: var(--accent); line-height: 1.1;">
                {{ total }}
            </div>
        </div>

        <div class="flex-end gap-8" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border);">
            <button type="button" class="btn btn-ghost" onclick="closeDiceRollerModal()">Close</button>
            <button type="button" class="btn btn-ghost" onclick="resetDiceRoller()">Roll Again</button>
        </div>
        {% endif %}
    </div>
</div>

<script>
    function selectDiceType(button, value) {
        document.querySelectorAll('#dice-roller-modal .toggle-group .btn').forEach(b => b.classList.remove('active'));
        button.classList.add('active');
        document.getElementById('dice-type-input').value = value;
        updateDicePreview();
    }

    function updateDicePreview() {
        const n = document.getElementById('num-dice-input')?.value || 1;
        const t = document.getElementById('dice-type-input')?.value || 20;
        const m = parseInt(document.getElementById('modifier-input')?.value || 0);
        const el = document.getElementById('roll-preview-display');
        if (!el) return;
        let text = n + 'd' + t;
        if (m > 0) text += ' +' + m;
        else if (m < 0) text += ' ' + m;
        el.textContent = text;
    }

    function closeDiceRollerModal() {
        const modal = document.getElementById('dice-roller-modal');
        if (modal) modal.classList.remove('active');
        htmx.trigger(document.body, 'dice-roller-closed');
    }

    function resetDiceRoller() {
        htmx.ajax('GET', '{% url "dice-roller-modal" game.id %}', {
            target: '#dice-roller-modal', swap: 'outerHTML'
        });
    }

    document.addEventListener('input', function(e) {
        if (['num-dice-input', 'modifier-input'].includes(e.target.id)) updateDicePreview();
    });
</script>
```

**Step 2: Replace `concentration_save_modal.html`**

```html
{% load static %}

<div id="concentration-save-modal" class="rpg-modal {% if show_modal %}active{% endif %}">
    <div class="modal-content">
        <button class="modal-close" onclick="closeConcentrationModal()" type="button">&times;</button>

        {% if not show_result %}
        <div class="modal-header">Concentration Check</div>

        <div style="font-size: 13px; margin-bottom: 16px;">
            <strong>{{ character.name }}</strong> must make a Constitution save
            to maintain <strong>{{ concentration.spell.name }}</strong>.
        </div>

        <div style="display: flex; flex-direction: column; gap: 6px; font-size: 13px; margin-bottom: 16px;">
            <div class="flex-between">
                <span class="text-muted">Damage taken</span>
                <span style="color: var(--red);">{{ damage }}</span>
            </div>
            <div class="flex-between">
                <span class="text-muted">Save DC</span>
                <span style="font-weight: 600; color: var(--text);">{{ dc }}</span>
            </div>
            <div class="flex-between">
                <span class="text-muted">Constitution modifier</span>
                <span>{% if con_modifier >= 0 %}+{% endif %}{{ con_modifier }}</span>
            </div>
        </div>

        <form hx-post="{% url 'concentration-save-roll' game.id character.pk %}"
              hx-target="#concentration-save-modal"
              hx-swap="outerHTML">
            <input type="hidden" name="dc" value="{{ dc }}">
            <input type="hidden" name="con_modifier" value="{{ con_modifier }}">
            <div class="flex-end gap-8">
                <button type="button" class="btn btn-ghost" onclick="closeConcentrationModal()">Skip</button>
                <button type="submit" class="btn btn-primary">Roll Save</button>
            </div>
        </form>

        {% else %}
        <div class="modal-header">
            {% if success %}Concentration Maintained{% else %}Concentration Lost{% endif %}
        </div>

        <div style="text-align: center; padding: 8px 0 16px;">
            <div class="text-mono" style="font-size: 48px; font-weight: 700;
                color: {% if success %}var(--green){% else %}var(--red){% endif %}; line-height: 1;">
                {{ roll }}
            </div>
            <div class="text-muted" style="font-size: 13px; margin-top: 8px;">
                {{ roll }} {% if con_modifier >= 0 %}+{% endif %}{{ con_modifier }} = <strong style="color: var(--text);">{{ total }}</strong>
                vs DC {{ dc }}
            </div>
            <div style="margin-top: 12px;">
                {% if is_natural_20 %}
                    <span class="badge badge-green" style="font-size: 14px; padding: 4px 12px;">Natural 20!</span>
                {% elif is_natural_1 %}
                    <span class="badge badge-red" style="font-size: 14px; padding: 4px 12px;">Natural 1</span>
                {% elif success %}
                    <span class="badge badge-green" style="font-size: 14px; padding: 4px 12px;">Success</span>
                {% else %}
                    <span class="badge badge-red" style="font-size: 14px; padding: 4px 12px;">Failed</span>
                {% endif %}
            </div>
            <div class="text-muted" style="font-size: 12px; margin-top: 8px;">
                {% if success %}
                    {{ character.name }} maintains concentration on {{ spell_name }}.
                {% else %}
                    {{ character.name }} has lost concentration on {{ spell_name }}.
                {% endif %}
            </div>
        </div>

        <div class="flex-end" style="padding-top: 16px; border-top: 1px solid var(--border);">
            <button type="button" class="btn btn-ghost" onclick="closeConcentrationModal()">Close</button>
        </div>
        {% endif %}
    </div>
</div>

<script>
    function closeConcentrationModal() {
        const modal = document.getElementById('concentration-save-modal');
        if (modal) modal.classList.remove('active');
        htmx.trigger(document.body, 'concentration-modal-closed');
    }
</script>
```

**Step 3: Run tests and verify**

```bash
doppler run -- uv run poe test
```

**Step 4: Commit**

```bash
git add game/templates/game/partials/dice_roller_modal.html \
        game/templates/game/partials/concentration_save_modal.html
git commit -m "style: simplify dice roller and concentration save modals"
```

---

## Task 9: Home Page

**Files:**
- Replace: `game/templates/game/index.html`

**Step 1: Replace `index.html`**

```html
{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="rpg-container" style="max-width: 600px; padding-top: 48px;">

    <h1 style="font-size: 24px; margin-bottom: 8px;">Role Play</h1>
    <p class="text-muted" style="margin-bottom: 32px;">
        A virtual tabletop for D&amp;D 5th Edition
        (<a href="https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf"
            style="color: var(--accent);" target="_blank" rel="noopener noreferrer">SRD 5.2.1</a>).
    </p>

    {% if user.is_authenticated %}
        <p style="margin-bottom: 24px; font-size: 14px;">Welcome back, {{ user.username }}.</p>

        <div class="action-buttons" style="gap: 8px;">
            {% if user_character_game %}
                <a href="{{ user_character_game.get_absolute_url }}" class="btn btn-primary">
                    Continue: {{ user_character_game }} ▸
                </a>
            {% endif %}
            {% if user_has_created_games %}
                <a href="{% url 'game-list' %}" class="btn btn-ghost">All games</a>
            {% endif %}
            {% if user_character %}
                <a href="{{ user_character.get_absolute_url }}" class="btn btn-ghost">My character</a>
            {% else %}
                <a href="{% url 'character-create' %}" class="btn btn-ghost">Create character</a>
            {% endif %}
            <a href="{% url 'campaign-create' %}" class="btn btn-ghost">Create a game</a>
        </div>
    {% else %}
        <div class="action-buttons">
            <a href="{% url 'login' %}" class="btn btn-primary">Log in</a>
            <a href="https://github.com/egraba/role-play" class="btn btn-ghost"
               target="_blank" rel="noopener noreferrer">GitHub ↗</a>
        </div>
    {% endif %}

</div>
{% endblock %}
```

**Step 2: Run tests and verify**

```bash
doppler run -- uv run poe test
```

**Step 3: Commit**

```bash
git add game/templates/game/index.html
git commit -m "style: home page — minimal welcome, remove marketing copy"
```

---

## Task 10: Game List and Small Form Pages

**Files:**
- Modify: `game/templates/game/game_list.html`
- Modify: `game/templates/game/game_start.html`
- Modify: `game/templates/game/quest_create.html`
- Modify: `game/templates/game/combat_create.html`
- Modify: `game/templates/game/user_invite.html`
- Modify: `game/templates/game/user_invite_confirm.html`
- Modify: `game/templates/game/ability_check_request.html`
- Modify: `game/templates/game/game_create.html`

All small form pages follow the same pattern: remove the inner `rpg-icon` from headings, ensure buttons use `.btn` classes. The `rpg-panel` and `rpg-container` classes already render correctly (legacy aliases in CSS). This task is about removing the heavy inline styles.

**Step 1: Update `game_list.html`**

The table is already using `.rpg-table` which now has clean styles. Remove the inner panel icon from the heading and the "Return to main menu" link:

```diff
-<h1 id="title" class="panel-title" style="font-size: 2rem;"><img src="/static/images/icons/actions/roll.svg" alt="" class="rpg-icon rpg-icon-lg rpg-icon-primary"> Games</h1>
-<div class="text-center mb-2">
-    <a href="{% url 'index' %}" style="color: var(--color-primary); text-decoration: underline;">Return to main menu</a>
-</div>
+<h1 class="panel-title">Games</h1>
```

Update the game name link:
```diff
-<td><a href="{{ game.get_absolute_url }}" style="color: var(--color-primary); text-decoration: underline;">{{ game }}</a></td>
+<td><a href="{{ game.get_absolute_url }}" style="color: var(--accent);">{{ game }}</a></td>
```

**Step 2: Update the small form pages**

For each of `game_start.html`, `quest_create.html`, `combat_create.html`, `user_invite.html`, `user_invite_confirm.html`, `ability_check_request.html`, `game_create.html`:
- Remove `<img>` icons from `<h1>` headings
- Replace any `style="..."` on buttons with `.btn .btn-primary` or `.btn .btn-ghost` classes
- Remove `max-width` inline styles on the outer panel (the `container` class handles this)

Example for `game_start.html`:
```diff
-<h1 class="panel-title"><img src="/static/images/icons/ui/play.svg" alt="" class="rpg-icon rpg-icon-lg rpg-icon-success"> Start Game</h1>
+<h1 class="panel-title">Start Game</h1>
```

```diff
-<button class="rpg-btn btn-primary" type="submit" style="width: 100%; box-sizing: border-box;">Yes, start it</button>
-<a href="{{ game.get_absolute_url }}" class="rpg-btn btn-defend" style="...">No, go back</a>
+<button class="btn btn-primary" type="submit">Yes, start it</button>
+<a href="{{ game.get_absolute_url }}" class="btn btn-ghost">No, go back</a>
```

**Step 3: Run tests and verify all pages**

```bash
doppler run -- uv run poe test
```

Spot-check: game list, game start confirmation, quest create form.

**Step 4: Commit**

```bash
git add game/templates/game/game_list.html \
        game/templates/game/game_start.html \
        game/templates/game/quest_create.html \
        game/templates/game/combat_create.html \
        game/templates/game/user_invite.html \
        game/templates/game/user_invite_confirm.html \
        game/templates/game/ability_check_request.html \
        game/templates/game/game_create.html
git commit -m "style: game list and form pages — remove icons from headings, clean buttons"
```

---

## Task 11: Quick Reference and Cleanup

**Files:**
- Modify: `game/static/css/quick-reference.css`
- Check: remove all remaining legacy `--color-*` variable references from inline styles

**Step 1: Strip animations and heavy chrome from `quick-reference.css`**

Open `game/static/css/quick-reference.css`. Remove:
- Any `@keyframes` animations
- Any `box-shadow` with blur > 4px
- Any `background: linear-gradient(...)`
- Change `font-family: 'Georgia'` to `font-family: system-ui`
- Change hardcoded `#d4af37` / `#1a1a2e` etc. to use `var(--accent)` / `var(--bg)` / `var(--border)`

**Step 2: Remove legacy CSS variable aliases from `rpg-styles.css`**

Once all templates have been updated (Tasks 2–10 complete), remove the legacy alias block from `rpg-styles.css`:

```css
/* Remove this entire block: */
--color-primary:    var(--accent);
--color-border:     var(--border);
...
```

Search for any remaining uses of old variable names:
```bash
grep -r "var(--color-" game/templates/ game/static/
```

Fix any remaining occurrences.

**Step 3: Run full test suite**

```bash
doppler run -- uv run poe test
pre-commit run --all-files
```

Expected: all tests pass, all pre-commit checks pass.

**Step 4: Final visual check**

Start the dev server:
```bash
doppler run -- uv run poe dev-run
```

Walk through the full game workflow:
1. Home page (logged out) → log in
2. Game list → click a game
3. Game screen — verify two-column layout, game log in left column
4. Send a message — appears in game log
5. Roll dice — modal opens, result shows, appears in log
6. Combat: initiative tracker and action panel appear in right column
7. Attack: modal opens, d20 result shows as large number, damage applied

**Step 5: Commit and push**

```bash
git add game/static/css/quick-reference.css game/static/css/rpg-styles.css
git commit -m "style: remove legacy CSS aliases and strip quick-reference animations"
```

Create a PR per project workflow.

---

## Summary

| Task | Files | Key change |
|---|---|---|
| 1 | `rpg-styles.css` | Full design system replacement |
| 2 | `base.html` | Navbar — remove per-link icons |
| 3 | `game.html` | Two-column layout |
| 4 | `game_log_panel.html`, `game-log.css`, `game-log.js` | Log as inline column |
| 5 | `initiative_tracker.html` | Strip `<style>` block, inline DM controls |
| 6 | `action_panel.html` | Strip `<style>` block, four-row layout |
| 7 | `attack_modal.html` | Strip `<style>` block, plain number result |
| 8 | `dice_roller_modal.html`, `concentration_save_modal.html` | Strip animations |
| 9 | `index.html` | Minimal welcome page |
| 10 | Game list + form pages | Remove icons from headings, clean buttons |
| 11 | `quick-reference.css`, cleanup | Remove legacy aliases, final polish |

**No Python files changed. No new tests needed. Run `doppler run -- uv run poe test` after each task.**
