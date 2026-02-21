# Home Screen Feature Grid Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an evocative tagline and 3-column feature grid to the home screen's anonymous/logged-out view so new visitors understand what Role Play is.

**Architecture:** Single template change to `game/templates/game/index.html`. The anonymous section gains a tagline paragraph and a CSS grid of three feature tiles (Characters, Combat, Stories). The authenticated section is untouched. No backend changes, no new context data, no JS.

**Tech Stack:** Django templates, inline CSS using the existing design token variables (`--bg-surface`, `--accent`, `--border`, `--radius`, `--text-muted`)

---

### Task 1: Update home screen template with tagline and feature grid

**Files:**
- Modify: `game/templates/game/index.html`
- Test: `game/tests/views/test_common.py` (run existing tests — no new tests needed)

**Context:** The design system tokens are defined in `game/static/css/rpg-styles.css`. The relevant ones:
- `--bg-surface: #1a1a2e` — tile background
- `--accent: #c9a227` — gold, used for tile headings
- `--border: rgba(255,255,255,0.08)` — tile border
- `--radius: 4px` — border radius
- `--text-muted: #888888` — tile body text

The pre-commit hook `DjHTML` will auto-reformat the template. Always run `pre-commit run djhtml --files game/templates/game/index.html` before staging.

**Step 1: Verify baseline tests pass**

```bash
doppler run -- uv run pytest game/tests/views/test_common.py::TestIndexView -v
```

Expected: all 6 tests pass.

**Step 2: Replace the template**

Replace the entire contents of `game/templates/game/index.html` with:

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
                        Continue your game ▸
                    </a>
                {% endif %}
                {% if user_has_created_games %}
                    <a href="{% url 'game-list' %}" class="btn btn-ghost">View all your games</a>
                {% endif %}
                {% if user_character %}
                    <a href="{{ user_character.get_absolute_url }}" class="btn btn-ghost">View your character</a>
                {% else %}
                    <a href="{% url 'character-create' %}" class="btn btn-ghost">Create your character</a>
                {% endif %}
                <a href="{% url 'campaign-create' %}" class="btn btn-ghost">Create a game</a>
            </div>
        {% else %}
            <p style="margin-bottom: 32px; font-size: 15px; line-height: 1.7; color: var(--text-muted);">
                Enter a world of dice, darkness, and decisions.
            </p>

            <div class="action-buttons" style="margin-bottom: 40px;">
                <a href="{% url 'login' %}" class="btn btn-primary">Log in</a>
                <a href="https://github.com/egraba/role-play" class="btn btn-ghost"
                   target="_blank" rel="noopener noreferrer">GitHub ↗</a>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px;">
                <div style="background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px;">
                    <div style="font-size: 11px; font-weight: 600; color: var(--accent); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">⚔ Characters</div>
                    <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin: 0;">Build your hero. Choose class, background, and origin feat from the full SRD.</p>
                </div>
                <div style="background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px;">
                    <div style="font-size: 11px; font-weight: 600; color: var(--accent); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">🎲 Combat</div>
                    <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin: 0;">Fight to survive. Real-time turns, initiative rolls, and full SRD combat rules.</p>
                </div>
                <div style="background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px;">
                    <div style="font-size: 11px; font-weight: 600; color: var(--accent); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">📜 Stories</div>
                    <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin: 0;">Shape the world. Your master weaves quests while you make choices that matter.</p>
                </div>
            </div>
        {% endif %}

    </div>
{% endblock %}
```

**Step 3: Run DjHTML to format the template**

```bash
pre-commit run djhtml --files game/templates/game/index.html
```

Expected: Passed (with possible indentation fixes applied to the file).

**Step 4: Run the IndexView tests**

```bash
doppler run -- uv run pytest game/tests/views/test_common.py::TestIndexView -v
```

Expected: all 6 tests pass. Key assertions that must still hold:
- `test_content_anonymous_user`: `assertContains(response, "Log in")` ✓ (still present)
- `test_content_user_without_character`: `assertContains(response, "Create your character")` ✓
- `test_content_user_with_character_no_game`: `assertContains(response, "View your character")` ✓
- `test_content_user_with_character_existing_game`: `assertContains(response, "Continue your game")` ✓

If any test fails because `assertNotContains` matches new text — check the new text doesn't accidentally contain a forbidden string (e.g. "Create your character" in the feature tile text).

**Step 5: Run full test suite**

```bash
doppler run -- uv run poe test
```

Expected: all tests pass (1630+).

**Step 6: Commit**

```bash
git add game/templates/game/index.html
git commit -m "feat: home screen — add tagline and feature grid for new visitors"
```
