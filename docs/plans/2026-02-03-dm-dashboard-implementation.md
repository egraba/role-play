# DM Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a dedicated DM dashboard page with six panels for game management.

**Architecture:** New view module `game/views/dm_dashboard.py` with HTMX-powered panels. Two new models for encounter templates and session notes. Character model extended with location field.

**Tech Stack:** Django views, HTMX partials, existing WebSocket infrastructure, pytest with factories.

---

## Task 1: Add Location Field to Character Model

**Files:**
- Modify: `character/models/character.py:21-60`
- Create: `character/migrations/XXXX_add_location_field.py` (auto-generated)
- Test: `character/tests/models/test_character.py`

**Step 1: Write the failing test**

Add to `character/tests/models/test_character.py`:

```python
class TestCharacterLocation:
    def test_location_field_default_empty(self, db):
        from character.tests.factories import CharacterFactory
        character = CharacterFactory()
        assert character.location == ""

    def test_location_field_can_be_set(self, db):
        from character.tests.factories import CharacterFactory
        character = CharacterFactory(location="Guard Tower")
        assert character.location == "Guard Tower"
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test character/tests/models/test_character.py::TestCharacterLocation -v`

Expected: FAIL with "Character() got an unexpected keyword argument 'location'"

**Step 3: Add location field to Character model**

In `character/models/character.py`, add after line 58 (after `inventory` field):

```python
    location = models.CharField(max_length=100, blank=True, default="")
```

**Step 4: Create and run migration**

Run: `doppler run -- python manage.py makemigrations character --name add_location_field`
Run: `doppler run -- python manage.py migrate`

**Step 5: Run test to verify it passes**

Run: `doppler run -- uv run poe test character/tests/models/test_character.py::TestCharacterLocation -v`

Expected: PASS

**Step 6: Commit**

```bash
git add character/models/character.py character/migrations/*_add_location_field.py character/tests/models/test_character.py
git commit -m "$(cat <<'EOF'
feat(character): add location field for DM tracking

Adds optional location field to Character model for DM dashboard
party overview panel.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Create SessionNote Model

**Files:**
- Create: `game/models/notes.py`
- Modify: `game/models/__init__.py`
- Create: `game/migrations/XXXX_add_session_note.py` (auto-generated)
- Test: `game/tests/models/test_notes.py`

**Step 1: Write the failing test**

Create `game/tests/models/test_notes.py`:

```python
import pytest

from game.models.notes import SessionNote
from game.tests.factories import GameFactory

pytestmark = pytest.mark.django_db


class TestSessionNote:
    def test_create_session_note(self):
        game = GameFactory()
        note = SessionNote.objects.create(game=game, content="Test notes")
        assert note.content == "Test notes"
        assert note.game == game

    def test_session_note_one_per_game(self):
        game = GameFactory()
        SessionNote.objects.create(game=game, content="First")
        with pytest.raises(Exception):  # IntegrityError
            SessionNote.objects.create(game=game, content="Second")

    def test_session_note_default_empty_content(self):
        game = GameFactory()
        note = SessionNote.objects.create(game=game)
        assert note.content == ""

    def test_session_note_updated_at_auto(self):
        game = GameFactory()
        note = SessionNote.objects.create(game=game, content="Test")
        assert note.updated_at is not None

    def test_session_note_str(self):
        game = GameFactory()
        note = SessionNote.objects.create(game=game, content="Test")
        assert str(note) == f"Session notes for {game.name}"
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test game/tests/models/test_notes.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'game.models.notes'"

**Step 3: Create SessionNote model**

Create `game/models/notes.py`:

```python
from django.db import models


class SessionNote(models.Model):
    """Session notes for a game, editable by the DM."""

    game = models.OneToOneField(
        "game.Game",
        on_delete=models.CASCADE,
        related_name="session_note",
    )
    content = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "session note"
        verbose_name_plural = "session notes"

    def __str__(self):
        return f"Session notes for {self.game.name}"
```

**Step 4: Update models __init__.py**

Add to `game/models/__init__.py`:

```python
from .notes import SessionNote

__all__ = ["SessionNote"]
```

**Step 5: Create and run migration**

Run: `doppler run -- python manage.py makemigrations game --name add_session_note`
Run: `doppler run -- python manage.py migrate`

**Step 6: Run test to verify it passes**

Run: `doppler run -- uv run poe test game/tests/models/test_notes.py -v`

Expected: PASS

**Step 7: Commit**

```bash
git add game/models/notes.py game/models/__init__.py game/migrations/*_add_session_note.py game/tests/models/test_notes.py
git commit -m "$(cat <<'EOF'
feat(game): add SessionNote model for DM notes

One-to-one with Game, stores DM session notes with auto-updated timestamp.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Create EncounterTemplate Models

**Files:**
- Create: `game/models/encounters.py`
- Modify: `game/models/__init__.py`
- Create: `game/migrations/XXXX_add_encounter_templates.py` (auto-generated)
- Test: `game/tests/models/test_encounters.py`

**Step 1: Write the failing test**

Create `game/tests/models/test_encounters.py`:

```python
import pytest

from game.models.encounters import EncounterTemplate, EncounterTemplateMonster
from game.tests.factories import GameFactory
from character.tests.factories import MonsterSettingsFactory

pytestmark = pytest.mark.django_db


class TestEncounterTemplate:
    def test_create_encounter_template(self):
        game = GameFactory()
        template = EncounterTemplate.objects.create(
            name="Goblin Ambush",
            game=game,
            description="A group of goblins attacks from the trees.",
        )
        assert template.name == "Goblin Ambush"
        assert template.game == game

    def test_encounter_template_str(self):
        game = GameFactory()
        template = EncounterTemplate.objects.create(name="Test", game=game)
        assert str(template) == "Test"


class TestEncounterTemplateMonster:
    def test_add_monster_to_template(self):
        game = GameFactory()
        template = EncounterTemplate.objects.create(name="Test", game=game)
        monster_settings = MonsterSettingsFactory()

        entry = EncounterTemplateMonster.objects.create(
            template=template,
            monster_settings=monster_settings,
            count=4,
        )
        assert entry.count == 4
        assert entry.template == template
        assert entry.monster_settings == monster_settings

    def test_template_monsters_related_name(self):
        game = GameFactory()
        template = EncounterTemplate.objects.create(name="Test", game=game)
        monster_settings = MonsterSettingsFactory()
        EncounterTemplateMonster.objects.create(
            template=template, monster_settings=monster_settings, count=2
        )
        assert template.monsters.count() == 1

    def test_encounter_template_monster_str(self):
        game = GameFactory()
        template = EncounterTemplate.objects.create(name="Ambush", game=game)
        monster_settings = MonsterSettingsFactory()
        entry = EncounterTemplateMonster.objects.create(
            template=template, monster_settings=monster_settings, count=3
        )
        assert str(entry) == f"3x {monster_settings.name} in Ambush"
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test game/tests/models/test_encounters.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'game.models.encounters'"

**Step 3: Create EncounterTemplate models**

Create `game/models/encounters.py`:

```python
from django.db import models


class EncounterTemplate(models.Model):
    """Pre-built encounter template for quick combat setup."""

    name = models.CharField(max_length=100)
    game = models.ForeignKey(
        "game.Game",
        on_delete=models.CASCADE,
        related_name="encounter_templates",
    )
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "encounter template"
        verbose_name_plural = "encounter templates"

    def __str__(self):
        return self.name


class EncounterTemplateMonster(models.Model):
    """Monster entry within an encounter template."""

    template = models.ForeignKey(
        EncounterTemplate,
        on_delete=models.CASCADE,
        related_name="monsters",
    )
    monster_settings = models.ForeignKey(
        "character.MonsterSettings",
        on_delete=models.CASCADE,
    )
    count = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["monster_settings__name"]
        verbose_name = "encounter template monster"
        verbose_name_plural = "encounter template monsters"

    def __str__(self):
        return f"{self.count}x {self.monster_settings.name} in {self.template.name}"
```

**Step 4: Update models __init__.py**

Add to `game/models/__init__.py`:

```python
from .encounters import EncounterTemplate, EncounterTemplateMonster
```

**Step 5: Create and run migration**

Run: `doppler run -- python manage.py makemigrations game --name add_encounter_templates`
Run: `doppler run -- python manage.py migrate`

**Step 6: Run test to verify it passes**

Run: `doppler run -- uv run poe test game/tests/models/test_encounters.py -v`

Expected: PASS

**Step 7: Commit**

```bash
git add game/models/encounters.py game/models/__init__.py game/migrations/*_add_encounter_templates.py game/tests/models/test_encounters.py
git commit -m "$(cat <<'EOF'
feat(game): add EncounterTemplate models

EncounterTemplate stores pre-built encounter setups.
EncounterTemplateMonster links monsters with counts to templates.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Create DM Dashboard View and URL

**Files:**
- Create: `game/views/dm_dashboard.py`
- Modify: `game/urls.py`
- Create: `game/templates/game/dm_dashboard.html`
- Test: `game/tests/views/test_dm_dashboard.py`

**Step 1: Write the failing test**

Create `game/tests/views/test_dm_dashboard.py`:

```python
import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from game.tests.factories import GameFactory, PlayerFactory
from game.flows import GameFlow

pytestmark = pytest.mark.django_db


@pytest.fixture
def started_game():
    game = GameFactory()
    for _ in range(2):
        PlayerFactory(game=game)
    flow = GameFlow(game)
    flow.start()
    return game


class TestDMDashboardView:
    path_name = "dm-dashboard"

    def test_master_can_access_dashboard(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200

    def test_player_cannot_access_dashboard(self, client, started_game):
        player = started_game.player_set.first()
        client.force_login(player.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 403

    def test_anonymous_cannot_access_dashboard(self, client, started_game):
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 302  # Redirect to login

    def test_dashboard_uses_correct_template(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assertTemplateUsed(response, "game/dm_dashboard.html")

    def test_dashboard_context_contains_game(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.context["game"] == started_game

    def test_dashboard_context_contains_characters(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert "characters" in response.context
        assert len(response.context["characters"]) == 2
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMDashboardView -v`

Expected: FAIL with "NoReverseMatch: Reverse for 'dm-dashboard' not found"

**Step 3: Create DM Dashboard view**

Create `game/views/dm_dashboard.py`:

```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

from character.models.character import Character

from .mixins import GameContextMixin


class DMDashboardView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, TemplateView
):
    """Main DM Dashboard view with all management panels."""

    template_name = "game/dm_dashboard.html"

    def test_func(self):
        return self.is_user_master()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all characters in this game
        characters = Character.objects.filter(
            player__game=self.game
        ).select_related(
            "player", "species"
        ).prefetch_related(
            "active_conditions__condition"
        )

        context["characters"] = characters
        return context
```

**Step 4: Add URL pattern**

In `game/urls.py`, add import and URL pattern:

After line 11, add:
```python
from .views import dm_dashboard
```

After the combat-end URL (around line 72), add:
```python
    path(
        "<int:game_id>/dm/",
        dm_dashboard.DMDashboardView.as_view(),
        name="dm-dashboard",
    ),
```

**Step 5: Create dashboard template**

Create `game/templates/game/dm_dashboard.html`:

```html
{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="dm-dashboard">
    <div class="dashboard-header">
        <h1 class="panel-title">
            <img src="{% static 'images/icons/actions/persuade.svg' %}" alt="" class="rpg-icon rpg-icon-xl rpg-icon-warning">
            DM Dashboard: {{ game.name }}
        </h1>
        <a href="{% url 'game' game.id %}" class="rpg-btn btn-secondary">Back to Game</a>
    </div>

    <div class="dashboard-grid">
        <!-- Row 1 -->
        <div class="dashboard-panel" id="party-panel">
            <h2 class="panel-title">Party Overview</h2>
            <div hx-get="{% url 'dm-party' game.id %}"
                 hx-trigger="load, party-updated from:body"
                 hx-swap="innerHTML">
                Loading...
            </div>
        </div>

        <div class="dashboard-panel" id="initiative-panel">
            <h2 class="panel-title">Initiative Tracker</h2>
            <div hx-get="{% url 'dm-initiative' game.id %}"
                 hx-trigger="load, initiative-updated from:body"
                 hx-swap="innerHTML">
                Loading...
            </div>
        </div>

        <!-- Row 2 -->
        <div class="dashboard-panel" id="monsters-panel">
            <h2 class="panel-title">Monster Quick-Add</h2>
            <div hx-get="{% url 'dm-monsters' game.id %}"
                 hx-trigger="load"
                 hx-swap="innerHTML">
                Loading...
            </div>
        </div>

        <div class="dashboard-panel" id="encounters-panel">
            <h2 class="panel-title">Encounter Manager</h2>
            <div hx-get="{% url 'dm-encounters' game.id %}"
                 hx-trigger="load, encounters-updated from:body"
                 hx-swap="innerHTML">
                Loading...
            </div>
        </div>

        <!-- Row 3 -->
        <div class="dashboard-panel" id="notes-panel">
            <h2 class="panel-title">Session Notes</h2>
            <div hx-get="{% url 'dm-notes' game.id %}"
                 hx-trigger="load"
                 hx-swap="innerHTML">
                Loading...
            </div>
        </div>

        <div class="dashboard-panel" id="secret-rolls-panel">
            <h2 class="panel-title">Secret Rolls</h2>
            <div hx-get="{% url 'dm-secret-rolls' game.id %}"
                 hx-trigger="load"
                 hx-swap="innerHTML">
                Loading...
            </div>
        </div>
    </div>
</div>

<style>
.dm-dashboard {
    padding: 20px;
    max-width: 1800px;
    margin: 0 auto;
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid var(--color-border);
}

.dashboard-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: repeat(3, minmax(250px, auto));
    gap: 20px;
}

.dashboard-panel {
    background: rgba(0, 0, 0, 0.4);
    border: 2px solid var(--color-border);
    border-radius: 8px;
    padding: 15px;
    overflow: auto;
}

.dashboard-panel .panel-title {
    font-size: 1.1rem;
    margin: 0 0 15px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--color-primary);
}

@media (max-width: 1200px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
}
</style>
{% endblock %}
```

**Step 6: Run test to verify it passes**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMDashboardView -v`

Expected: PASS

**Step 7: Commit**

```bash
git add game/views/dm_dashboard.py game/urls.py game/templates/game/dm_dashboard.html game/tests/views/test_dm_dashboard.py
git commit -m "$(cat <<'EOF'
feat(game): add DM dashboard main view and template

Creates /game/<id>/dm/ route with 2x3 grid layout for DM panels.
Master-only access with proper permission checks.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Create Party Overview Panel

**Files:**
- Modify: `game/views/dm_dashboard.py`
- Modify: `game/urls.py`
- Create: `game/templates/game/partials/dm_party.html`
- Test: `game/tests/views/test_dm_dashboard.py`

**Step 1: Write the failing test**

Add to `game/tests/views/test_dm_dashboard.py`:

```python
class TestDMPartyPanelView:
    path_name = "dm-party"

    def test_master_can_access_party_panel(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200

    def test_party_panel_shows_characters(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        characters = started_game.player_set.values_list("character__name", flat=True)
        for name in characters:
            assert name in response.content.decode()

    def test_party_panel_shows_hp(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        content = response.content.decode()
        # Should show HP values
        assert "hp" in content.lower() or "/" in content


class TestDMUpdateLocationView:
    path_name = "dm-update-location"

    def test_master_can_update_location(self, client, started_game):
        client.force_login(started_game.master.user)
        character = started_game.player_set.first().character
        response = client.post(
            reverse(self.path_name, args=(started_game.id, character.id)),
            data={"location": "Guard Tower"},
        )
        assert response.status_code == 200
        character.refresh_from_db()
        assert character.location == "Guard Tower"
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMPartyPanelView -v`

Expected: FAIL with "NoReverseMatch: Reverse for 'dm-party' not found"

**Step 3: Add Party Panel view to dm_dashboard.py**

Add to `game/views/dm_dashboard.py`:

```python
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from character.models.spells import Concentration


class DMPartyPanelView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """HTMX partial for party overview panel."""

    def test_func(self):
        return self.is_user_master()

    def get(self, request, *args, **kwargs):
        characters_data = []
        characters = Character.objects.filter(
            player__game=self.game
        ).select_related(
            "player__user", "species"
        ).prefetch_related(
            "active_conditions__condition"
        )

        for character in characters:
            try:
                concentration = character.concentration
            except Concentration.DoesNotExist:
                concentration = None

            characters_data.append({
                "character": character,
                "hp": character.hp,
                "max_hp": character.max_hp,
                "hp_percentage": character.hp_percentage,
                "conditions": list(character.active_conditions.all()),
                "concentration": concentration,
                "location": character.location,
            })

        context = {
            "game": self.game,
            "characters": characters_data,
        }
        html = render_to_string("game/partials/dm_party.html", context, request)
        return HttpResponse(html)


class DMUpdateLocationView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """Update character location via HTMX."""

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        character_id = kwargs.get("character_id")
        character = Character.objects.get(
            id=character_id, player__game=self.game
        )
        character.location = request.POST.get("location", "")
        character.save(update_fields=["location"])

        return HttpResponse(character.location or "Not set")
```

**Step 4: Add URL patterns**

Add to `game/urls.py` after dm-dashboard URL:

```python
    path(
        "<int:game_id>/dm/party/",
        dm_dashboard.DMPartyPanelView.as_view(),
        name="dm-party",
    ),
    path(
        "<int:game_id>/dm/party/<int:character_id>/location/",
        dm_dashboard.DMUpdateLocationView.as_view(),
        name="dm-update-location",
    ),
```

**Step 5: Create party panel template**

Create `game/templates/game/partials/dm_party.html`:

```html
<div class="party-list">
    {% for data in characters %}
    <div class="party-member">
        <div class="member-header">
            <a href="{{ data.character.get_absolute_url }}"
               target="_blank"
               class="member-name">
                {{ data.character.name }}
            </a>
            <span class="member-class">
                {{ data.character.primary_class|default:"No class" }}
            </span>
        </div>

        <div class="member-hp">
            <div class="hp-bar-container">
                <div class="hp-bar {% if data.hp_percentage <= 25 %}critical{% elif data.hp_percentage <= 50 %}warning{% endif %}"
                     style="width: {{ data.hp_percentage }}%">
                </div>
            </div>
            <span class="hp-text">{{ data.hp }}/{{ data.max_hp }}</span>
        </div>

        <div class="member-status">
            {% if data.concentration %}
                <span class="concentration-badge" title="Concentrating on {{ data.concentration.spell.name }}">
                    &#9673; {{ data.concentration.spell.name }}
                </span>
            {% endif %}
            {% for char_condition in data.conditions %}
                <span class="condition-badge" title="{{ char_condition.condition.description }}">
                    {{ char_condition.condition.name }}
                </span>
            {% endfor %}
        </div>

        <div class="member-location">
            <label>Location:</label>
            <input type="text"
                   value="{{ data.location }}"
                   placeholder="Not set"
                   hx-post="{% url 'dm-update-location' game.id data.character.id %}"
                   hx-trigger="blur changed, keyup[key=='Enter']"
                   hx-swap="none"
                   class="location-input">
        </div>
    </div>
    {% empty %}
    <p class="text-muted">No characters in this game.</p>
    {% endfor %}
</div>

<style>
.party-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.party-member {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 6px;
    padding: 12px;
    border-left: 3px solid var(--color-border);
}

.member-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.member-name {
    font-weight: bold;
    color: var(--color-primary);
    text-decoration: none;
}

.member-name:hover {
    text-decoration: underline;
}

.member-class {
    font-size: 0.85rem;
    color: var(--color-text-muted);
}

.member-hp {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}

.hp-bar-container {
    flex: 1;
    height: 12px;
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid #444;
    border-radius: 6px;
    overflow: hidden;
}

.hp-bar {
    height: 100%;
    background: linear-gradient(90deg, #27ae60, var(--color-stamina));
    transition: width 0.3s ease;
}

.hp-bar.warning {
    background: linear-gradient(90deg, #e67e22, #f39c12);
}

.hp-bar.critical {
    background: linear-gradient(90deg, #c0392b, var(--color-health));
}

.hp-text {
    font-size: 0.9rem;
    min-width: 60px;
    text-align: right;
}

.member-status {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 8px;
}

.concentration-badge {
    background: rgba(155, 89, 182, 0.3);
    border: 1px solid #9b59b6;
    color: #9b59b6;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
}

.condition-badge {
    background: rgba(231, 76, 60, 0.3);
    border: 1px solid #e74c3c;
    color: #e74c3c;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
}

.member-location {
    display: flex;
    align-items: center;
    gap: 8px;
}

.member-location label {
    font-size: 0.85rem;
    color: var(--color-text-muted);
}

.location-input {
    flex: 1;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 4px 8px;
    color: var(--color-text);
    font-size: 0.85rem;
}

.location-input:focus {
    outline: none;
    border-color: var(--color-primary);
}
</style>
```

**Step 6: Run test to verify it passes**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMPartyPanelView game/tests/views/test_dm_dashboard.py::TestDMUpdateLocationView -v`

Expected: PASS

**Step 7: Commit**

```bash
git add game/views/dm_dashboard.py game/urls.py game/templates/game/partials/dm_party.html game/tests/views/test_dm_dashboard.py
git commit -m "$(cat <<'EOF'
feat(game): add party overview panel for DM dashboard

Shows all characters with HP bars, conditions, concentration status,
and editable location field with HTMX inline updates.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Create Initiative Tracker Panel for Dashboard

**Files:**
- Modify: `game/views/dm_dashboard.py`
- Modify: `game/urls.py`
- Create: `game/templates/game/partials/dm_initiative.html`
- Test: `game/tests/views/test_dm_dashboard.py`

**Step 1: Write the failing test**

Add to `game/tests/views/test_dm_dashboard.py`:

```python
from game.models.combat import Combat, Fighter
from game.constants.combat import CombatState


class TestDMInitiativePanelView:
    path_name = "dm-initiative"

    @pytest.fixture
    def active_combat(self, started_game):
        combat = Combat.objects.create(game=started_game)
        players = list(started_game.player_set.all())
        for i, player in enumerate(players):
            Fighter.objects.create(
                player=player,
                character=player.character,
                combat=combat,
                dexterity_check=15 - i,
            )
        combat.start_combat()
        return combat

    def test_master_can_access_initiative_panel(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200

    def test_shows_no_combat_message_when_inactive(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert "No active combat" in response.content.decode()

    def test_shows_initiative_order_during_combat(self, client, started_game, active_combat):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        content = response.content.decode()
        for fighter in active_combat.fighter_set.all():
            assert fighter.character.name in content
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMInitiativePanelView -v`

Expected: FAIL with "NoReverseMatch: Reverse for 'dm-initiative' not found"

**Step 3: Add Initiative Panel view**

Add to `game/views/dm_dashboard.py`:

```python
from ..models.combat import Combat
from ..constants.combat import CombatState
from .initiative import InitiativeTrackerMixin


class DMInitiativePanelView(
    LoginRequiredMixin, UserPassesTestMixin, InitiativeTrackerMixin, GameContextMixin, View
):
    """HTMX partial for initiative tracker in DM dashboard."""

    def test_func(self):
        return self.is_user_master()

    def get(self, request, *args, **kwargs):
        # Find active combat for this game
        combat = Combat.objects.filter(
            game=self.game,
            state=CombatState.ACTIVE
        ).first()

        if not combat:
            html = render_to_string(
                "game/partials/dm_initiative.html",
                {"game": self.game, "combat": None},
                request
            )
            return HttpResponse(html)

        context = self.get_tracker_context(combat, request.user)
        context["game"] = self.game
        context["is_dm"] = True

        html = render_to_string("game/partials/dm_initiative.html", context, request)
        return HttpResponse(html)
```

**Step 4: Add URL pattern**

Add to `game/urls.py`:

```python
    path(
        "<int:game_id>/dm/initiative/",
        dm_dashboard.DMInitiativePanelView.as_view(),
        name="dm-initiative",
    ),
```

**Step 5: Create initiative panel template**

Create `game/templates/game/partials/dm_initiative.html`:

```html
{% if not combat %}
<div class="no-combat">
    <p class="text-muted text-center">No active combat.</p>
    <div class="text-center">
        <a href="{% url 'combat-create' game.id %}" class="rpg-btn btn-attack">
            Start New Combat
        </a>
    </div>
</div>
{% else %}
<div class="dm-initiative-tracker">
    <div class="tracker-header">
        <div class="round-counter">
            <span class="round-label">Round</span>
            <span class="round-number">{{ current_round }}</span>
        </div>
    </div>

    <div class="combatant-list">
        {% for data in fighters %}
        <div class="combatant-row {% if data.is_current %}current-turn{% endif %}">
            <div class="initiative-badge">
                <span class="initiative-value">{{ data.initiative|default:"--" }}</span>
            </div>

            <div class="combatant-info">
                <span class="combatant-name">{{ data.character.name }}</span>
                <div class="mini-hp">
                    <div class="mini-hp-bar" style="width: {{ data.hp_percentage }}%"></div>
                    <span>{{ data.hp }}/{{ data.max_hp }}</span>
                </div>
            </div>

            <div class="combatant-conditions">
                {% if data.concentration %}
                <span class="conc-icon" title="{{ data.concentration.spell.name }}">&#9673;</span>
                {% endif %}
                {% for cond in data.conditions %}
                <span class="cond-icon" title="{{ cond.condition.name }}">!</span>
                {% endfor %}
            </div>

            {% if data.is_current %}
            <span class="turn-indicator">
                <span class="turn-dot"></span>
            </span>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <div class="dm-controls">
        <form action="{% url 'combat-advance-turn' game.id combat.id %}" method="post" style="display: inline;">
            {% csrf_token %}
            <button type="submit" class="rpg-btn btn-primary">Next Turn</button>
        </form>
        <form action="{% url 'combat-end' game.id combat.id %}" method="post" style="display: inline;">
            {% csrf_token %}
            <button type="submit" class="rpg-btn btn-danger">End Combat</button>
        </form>
    </div>
</div>

<style>
.no-combat {
    padding: 20px;
}

.dm-initiative-tracker {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.tracker-header {
    display: flex;
    justify-content: flex-end;
}

.round-counter {
    background: rgba(139, 69, 19, 0.3);
    border: 1px solid var(--color-primary);
    border-radius: 15px;
    padding: 4px 12px;
    display: flex;
    gap: 6px;
    align-items: center;
}

.round-label {
    font-size: 0.8rem;
    color: var(--color-text-muted);
}

.round-number {
    font-weight: bold;
    color: var(--color-primary);
}

.combatant-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.combatant-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 4px;
    border-left: 3px solid transparent;
}

.combatant-row.current-turn {
    border-left-color: var(--color-primary);
    background: rgba(139, 69, 19, 0.2);
}

.initiative-badge {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #2c3e50, #34495e);
    border: 1px solid var(--color-border);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 0.9rem;
}

.combatant-info {
    flex: 1;
    min-width: 0;
}

.combatant-name {
    display: block;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.mini-hp {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    color: var(--color-text-muted);
}

.mini-hp-bar {
    width: 60px;
    height: 4px;
    background: var(--color-stamina);
    border-radius: 2px;
}

.combatant-conditions {
    display: flex;
    gap: 4px;
}

.conc-icon {
    color: #9b59b6;
}

.cond-icon {
    color: #e74c3c;
}

.turn-indicator {
    width: 20px;
    display: flex;
    justify-content: center;
}

.turn-dot {
    width: 10px;
    height: 10px;
    background: var(--color-primary);
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.dm-controls {
    display: flex;
    gap: 10px;
    justify-content: center;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-danger {
    background: linear-gradient(135deg, #8b0000, #a52a2a);
    border-color: #e74c3c;
}
</style>
{% endif %}
```

**Step 6: Run test to verify it passes**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMInitiativePanelView -v`

Expected: PASS

**Step 7: Commit**

```bash
git add game/views/dm_dashboard.py game/urls.py game/templates/game/partials/dm_initiative.html game/tests/views/test_dm_dashboard.py
git commit -m "$(cat <<'EOF'
feat(game): add initiative tracker panel for DM dashboard

Shows current combat state with initiative order, HP, conditions.
Includes Next Turn and End Combat controls.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Create Monster Quick-Add Panel

**Files:**
- Modify: `game/views/dm_dashboard.py`
- Modify: `game/urls.py`
- Create: `game/templates/game/partials/dm_monsters.html`
- Test: `game/tests/views/test_dm_dashboard.py`

**Step 1: Write the failing test**

Add to `game/tests/views/test_dm_dashboard.py`:

```python
from character.tests.factories import MonsterSettingsFactory


class TestDMMonstersPanelView:
    path_name = "dm-monsters"

    def test_master_can_access_monsters_panel(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200


class TestDMMonsterSearchView:
    path_name = "dm-monster-search"

    def test_search_returns_matching_monsters(self, client, started_game):
        client.force_login(started_game.master.user)
        # MonsterSettings are loaded from fixtures, search for "goblin"
        response = client.get(
            reverse(self.path_name, args=(started_game.id,)),
            {"q": "goblin"}
        )
        assert response.status_code == 200

    def test_search_returns_empty_for_no_match(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(
            reverse(self.path_name, args=(started_game.id,)),
            {"q": "xyznonexistent"}
        )
        assert response.status_code == 200
        assert "No monsters found" in response.content.decode()
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMMonstersPanelView -v`

Expected: FAIL with "NoReverseMatch: Reverse for 'dm-monsters' not found"

**Step 3: Add Monster Panel views**

Add to `game/views/dm_dashboard.py`:

```python
from character.models.monsters import MonsterSettings


class DMMonstersPanelView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """HTMX partial for monster quick-add panel."""

    def test_func(self):
        return self.is_user_master()

    def get(self, request, *args, **kwargs):
        context = {"game": self.game}
        html = render_to_string("game/partials/dm_monsters.html", context, request)
        return HttpResponse(html)


class DMMonsterSearchView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """Search monsters by name."""

    def test_func(self):
        return self.is_user_master()

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()
        monsters = []

        if query:
            monsters = MonsterSettings.objects.filter(
                name__icontains=query
            )[:10]

        context = {
            "game": self.game,
            "monsters": monsters,
            "query": query,
        }
        html = render_to_string(
            "game/partials/dm_monster_results.html", context, request
        )
        return HttpResponse(html)
```

**Step 4: Add URL patterns**

Add to `game/urls.py`:

```python
    path(
        "<int:game_id>/dm/monsters/",
        dm_dashboard.DMMonstersPanelView.as_view(),
        name="dm-monsters",
    ),
    path(
        "<int:game_id>/dm/monsters/search/",
        dm_dashboard.DMMonsterSearchView.as_view(),
        name="dm-monster-search",
    ),
```

**Step 5: Create monster panel templates**

Create `game/templates/game/partials/dm_monsters.html`:

```html
<div class="monster-search">
    <input type="text"
           name="q"
           placeholder="Search monsters..."
           hx-get="{% url 'dm-monster-search' game.id %}"
           hx-trigger="keyup changed delay:300ms"
           hx-target="#monster-results"
           class="search-input">
</div>

<div id="monster-results">
    <p class="text-muted text-center">Type to search for monsters...</p>
</div>

<style>
.monster-search {
    margin-bottom: 15px;
}

.search-input {
    width: 100%;
    padding: 10px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    color: var(--color-text);
    font-size: 1rem;
}

.search-input:focus {
    outline: none;
    border-color: var(--color-primary);
}
</style>
```

Create `game/templates/game/partials/dm_monster_results.html`:

```html
{% if monsters %}
<div class="monster-list">
    {% for monster in monsters %}
    <div class="monster-card">
        <div class="monster-header">
            <span class="monster-name">{{ monster.name }}</span>
            <span class="monster-cr">CR {{ monster.challenge_rating }}</span>
        </div>
        <div class="monster-stats">
            <span>AC {{ monster.ac }}</span>
            <span>HP {{ monster.hp_average }}</span>
        </div>
        <div class="monster-actions">
            <button class="rpg-btn btn-sm btn-primary"
                    hx-post="{% url 'dm-add-monster-to-encounter' game.id %}"
                    hx-vals='{"monster": "{{ monster.name }}"}'
                    hx-swap="none">
                Add to Template
            </button>
        </div>
    </div>
    {% endfor %}
</div>
{% else %}
<p class="text-muted text-center">
    {% if query %}No monsters found matching "{{ query }}"{% else %}Type to search...{% endif %}
</p>
{% endif %}

<style>
.monster-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 300px;
    overflow-y: auto;
}

.monster-card {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 4px;
    padding: 10px;
    border-left: 3px solid var(--color-border);
}

.monster-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
}

.monster-name {
    font-weight: 600;
    color: var(--color-text);
}

.monster-cr {
    font-size: 0.85rem;
    color: var(--color-primary);
}

.monster-stats {
    font-size: 0.85rem;
    color: var(--color-text-muted);
    display: flex;
    gap: 15px;
    margin-bottom: 8px;
}

.monster-actions {
    display: flex;
    gap: 6px;
}

.btn-sm {
    padding: 4px 8px;
    font-size: 0.75rem;
}
</style>
```

**Step 6: Run test to verify it passes**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMMonstersPanelView game/tests/views/test_dm_dashboard.py::TestDMMonsterSearchView -v`

Expected: PASS

**Step 7: Commit**

```bash
git add game/views/dm_dashboard.py game/urls.py game/templates/game/partials/dm_monsters.html game/templates/game/partials/dm_monster_results.html game/tests/views/test_dm_dashboard.py
git commit -m "$(cat <<'EOF'
feat(game): add monster quick-add panel for DM dashboard

Type-ahead search of MonsterSettings database with CR, AC, HP display.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Create Encounter Manager Panel

**Files:**
- Modify: `game/views/dm_dashboard.py`
- Modify: `game/urls.py`
- Create: `game/templates/game/partials/dm_encounters.html`
- Create: `game/tests/factories.py` (add EncounterTemplateFactory)
- Test: `game/tests/views/test_dm_dashboard.py`

**Step 1: Write the failing test**

Add to `game/tests/views/test_dm_dashboard.py`:

```python
from game.models.encounters import EncounterTemplate, EncounterTemplateMonster


class TestDMEncountersPanelView:
    path_name = "dm-encounters"

    def test_master_can_access_encounters_panel(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200

    def test_shows_existing_templates(self, client, started_game):
        client.force_login(started_game.master.user)
        EncounterTemplate.objects.create(name="Goblin Ambush", game=started_game)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert "Goblin Ambush" in response.content.decode()


class TestDMCreateEncounterView:
    path_name = "dm-create-encounter"

    def test_create_encounter_template(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.post(
            reverse(self.path_name, args=(started_game.id,)),
            data={"name": "Test Encounter", "description": "A test"},
        )
        assert response.status_code == 200
        assert EncounterTemplate.objects.filter(
            game=started_game, name="Test Encounter"
        ).exists()


class TestDMAddMonsterToEncounterView:
    path_name = "dm-add-monster-to-encounter"

    def test_add_monster_to_template(self, client, started_game):
        client.force_login(started_game.master.user)
        template = EncounterTemplate.objects.create(name="Test", game=started_game)
        # Assumes GOBLIN exists in fixtures
        response = client.post(
            reverse(self.path_name, args=(started_game.id,)),
            data={"template_id": template.id, "monster": "GOBLIN", "count": 3},
        )
        assert response.status_code == 200
        assert template.monsters.filter(monster_settings__name="GOBLIN").exists()
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMEncountersPanelView -v`

Expected: FAIL with "NoReverseMatch: Reverse for 'dm-encounters' not found"

**Step 3: Add Encounter Panel views**

Add to `game/views/dm_dashboard.py`:

```python
from ..models.encounters import EncounterTemplate, EncounterTemplateMonster


class DMEncountersPanelView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """HTMX partial for encounter manager panel."""

    def test_func(self):
        return self.is_user_master()

    def get(self, request, *args, **kwargs):
        templates = EncounterTemplate.objects.filter(
            game=self.game
        ).prefetch_related("monsters__monster_settings")

        context = {
            "game": self.game,
            "templates": templates,
        }
        html = render_to_string("game/partials/dm_encounters.html", context, request)
        return HttpResponse(html)


class DMCreateEncounterView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """Create a new encounter template."""

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "")

        if name:
            EncounterTemplate.objects.create(
                name=name,
                game=self.game,
                description=description,
            )

        # Return updated panel
        return DMEncountersPanelView.as_view()(request, *args, **kwargs)


class DMAddMonsterToEncounterView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """Add a monster to an encounter template."""

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        template_id = request.POST.get("template_id")
        monster_name = request.POST.get("monster")
        count = int(request.POST.get("count", 1))

        template = EncounterTemplate.objects.get(id=template_id, game=self.game)
        monster_settings = MonsterSettings.objects.get(name=monster_name)

        # Check if this monster already exists in template
        entry, created = EncounterTemplateMonster.objects.get_or_create(
            template=template,
            monster_settings=monster_settings,
            defaults={"count": count},
        )
        if not created:
            entry.count += count
            entry.save()

        response = HttpResponse()
        response["HX-Trigger"] = "encounters-updated"
        return response
```

**Step 4: Add URL patterns**

Add to `game/urls.py`:

```python
    path(
        "<int:game_id>/dm/encounters/",
        dm_dashboard.DMEncountersPanelView.as_view(),
        name="dm-encounters",
    ),
    path(
        "<int:game_id>/dm/encounters/create/",
        dm_dashboard.DMCreateEncounterView.as_view(),
        name="dm-create-encounter",
    ),
    path(
        "<int:game_id>/dm/encounters/add-monster/",
        dm_dashboard.DMAddMonsterToEncounterView.as_view(),
        name="dm-add-monster-to-encounter",
    ),
```

**Step 5: Create encounters panel template**

Create `game/templates/game/partials/dm_encounters.html`:

```html
<div class="encounters-panel">
    <div class="new-encounter-form">
        <form hx-post="{% url 'dm-create-encounter' game.id %}"
              hx-target="#encounters-panel > div"
              hx-swap="innerHTML">
            {% csrf_token %}
            <div class="form-row">
                <input type="text" name="name" placeholder="Encounter name..." class="encounter-name-input" required>
                <button type="submit" class="rpg-btn btn-primary btn-sm">Create</button>
            </div>
        </form>
    </div>

    <div class="templates-list">
        {% for template in templates %}
        <div class="template-card">
            <div class="template-header">
                <span class="template-name">{{ template.name }}</span>
                <form action="{% url 'combat-create' game.id %}" method="get" style="display: inline;">
                    <input type="hidden" name="template" value="{{ template.id }}">
                    <button type="submit" class="rpg-btn btn-attack btn-sm">Load</button>
                </form>
            </div>
            {% if template.description %}
            <p class="template-desc">{{ template.description }}</p>
            {% endif %}
            <div class="template-monsters">
                {% for entry in template.monsters.all %}
                <span class="monster-tag">{{ entry.count }}x {{ entry.monster_settings.name }}</span>
                {% empty %}
                <span class="text-muted">No monsters added</span>
                {% endfor %}
            </div>
        </div>
        {% empty %}
        <p class="text-muted text-center">No encounter templates yet.</p>
        {% endfor %}
    </div>
</div>

<style>
.new-encounter-form {
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.form-row {
    display: flex;
    gap: 10px;
}

.encounter-name-input {
    flex: 1;
    padding: 8px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    color: var(--color-text);
}

.templates-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 300px;
    overflow-y: auto;
}

.template-card {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 4px;
    padding: 10px;
    border-left: 3px solid var(--color-primary);
}

.template-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.template-name {
    font-weight: 600;
}

.template-desc {
    font-size: 0.85rem;
    color: var(--color-text-muted);
    margin: 4px 0;
}

.template-monsters {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.monster-tag {
    background: rgba(139, 69, 19, 0.3);
    border: 1px solid var(--color-border);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
}
</style>
```

**Step 6: Run test to verify it passes**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMEncountersPanelView game/tests/views/test_dm_dashboard.py::TestDMCreateEncounterView game/tests/views/test_dm_dashboard.py::TestDMAddMonsterToEncounterView -v`

Expected: PASS

**Step 7: Commit**

```bash
git add game/views/dm_dashboard.py game/urls.py game/templates/game/partials/dm_encounters.html game/tests/views/test_dm_dashboard.py
git commit -m "$(cat <<'EOF'
feat(game): add encounter manager panel for DM dashboard

Create, view, and populate encounter templates with monsters.
Templates can be loaded into combat with one click.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Create Session Notes Panel

**Files:**
- Modify: `game/views/dm_dashboard.py`
- Modify: `game/urls.py`
- Create: `game/templates/game/partials/dm_notes.html`
- Test: `game/tests/views/test_dm_dashboard.py`

**Step 1: Write the failing test**

Add to `game/tests/views/test_dm_dashboard.py`:

```python
from game.models.notes import SessionNote


class TestDMNotesPanelView:
    path_name = "dm-notes"

    def test_master_can_access_notes_panel(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200

    def test_creates_session_note_if_not_exists(self, client, started_game):
        client.force_login(started_game.master.user)
        assert not SessionNote.objects.filter(game=started_game).exists()
        client.get(reverse(self.path_name, args=(started_game.id,)))
        assert SessionNote.objects.filter(game=started_game).exists()


class TestDMSaveNotesView:
    path_name = "dm-save-notes"

    def test_save_notes(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.post(
            reverse(self.path_name, args=(started_game.id,)),
            data={"content": "These are my session notes."},
        )
        assert response.status_code == 200
        note = SessionNote.objects.get(game=started_game)
        assert note.content == "These are my session notes."

    def test_save_notes_updates_existing(self, client, started_game):
        client.force_login(started_game.master.user)
        SessionNote.objects.create(game=started_game, content="Old notes")
        client.post(
            reverse(self.path_name, args=(started_game.id,)),
            data={"content": "New notes"},
        )
        note = SessionNote.objects.get(game=started_game)
        assert note.content == "New notes"
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMNotesPanelView -v`

Expected: FAIL with "NoReverseMatch: Reverse for 'dm-notes' not found"

**Step 3: Add Notes Panel views**

Add to `game/views/dm_dashboard.py`:

```python
from ..models.notes import SessionNote


class DMNotesPanelView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """HTMX partial for session notes panel."""

    def test_func(self):
        return self.is_user_master()

    def get(self, request, *args, **kwargs):
        note, _ = SessionNote.objects.get_or_create(game=self.game)

        context = {
            "game": self.game,
            "note": note,
        }
        html = render_to_string("game/partials/dm_notes.html", context, request)
        return HttpResponse(html)


class DMSaveNotesView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """Save session notes via HTMX."""

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        content = request.POST.get("content", "")
        note, _ = SessionNote.objects.get_or_create(game=self.game)
        note.content = content
        note.save()

        return HttpResponse(f"Saved at {note.updated_at.strftime('%H:%M')}")
```

**Step 4: Add URL patterns**

Add to `game/urls.py`:

```python
    path(
        "<int:game_id>/dm/notes/",
        dm_dashboard.DMNotesPanelView.as_view(),
        name="dm-notes",
    ),
    path(
        "<int:game_id>/dm/notes/save/",
        dm_dashboard.DMSaveNotesView.as_view(),
        name="dm-save-notes",
    ),
```

**Step 5: Create notes panel template**

Create `game/templates/game/partials/dm_notes.html`:

```html
<div class="notes-panel">
    <textarea id="session-notes"
              name="content"
              placeholder="Write your session notes here..."
              hx-post="{% url 'dm-save-notes' game.id %}"
              hx-trigger="blur, keyup changed delay:2000ms"
              hx-target="#save-status"
              hx-swap="innerHTML">{{ note.content }}</textarea>

    <div class="notes-footer">
        <span id="save-status" class="save-status">
            {% if note.updated_at %}
            Last saved: {{ note.updated_at|time:"H:i" }}
            {% endif %}
        </span>
    </div>
</div>

<style>
.notes-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
}

#session-notes {
    flex: 1;
    min-height: 200px;
    padding: 12px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    color: var(--color-text);
    font-family: monospace;
    font-size: 0.9rem;
    resize: vertical;
    line-height: 1.5;
}

#session-notes:focus {
    outline: none;
    border-color: var(--color-primary);
}

.notes-footer {
    display: flex;
    justify-content: flex-end;
    padding-top: 8px;
}

.save-status {
    font-size: 0.8rem;
    color: var(--color-text-muted);
}
</style>
```

**Step 6: Run test to verify it passes**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMNotesPanelView game/tests/views/test_dm_dashboard.py::TestDMSaveNotesView -v`

Expected: PASS

**Step 7: Commit**

```bash
git add game/views/dm_dashboard.py game/urls.py game/templates/game/partials/dm_notes.html game/tests/views/test_dm_dashboard.py
git commit -m "$(cat <<'EOF'
feat(game): add session notes panel for DM dashboard

Auto-saving textarea for DM notes with last-saved timestamp.
Creates SessionNote on first access, persists per game.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Create Secret Rolls Panel

**Files:**
- Modify: `game/views/dm_dashboard.py`
- Modify: `game/urls.py`
- Create: `game/templates/game/partials/dm_secret_rolls.html`
- Test: `game/tests/views/test_dm_dashboard.py`

**Step 1: Write the failing test**

Add to `game/tests/views/test_dm_dashboard.py`:

```python
class TestDMSecretRollsPanelView:
    path_name = "dm-secret-rolls"

    def test_master_can_access_secret_rolls_panel(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        assert response.status_code == 200

    def test_shows_character_list(self, client, started_game):
        client.force_login(started_game.master.user)
        response = client.get(reverse(self.path_name, args=(started_game.id,)))
        content = response.content.decode()
        for player in started_game.player_set.all():
            assert player.character.name in content


class TestDMSecretRollView:
    path_name = "dm-secret-roll"

    def test_roll_perception(self, client, started_game):
        client.force_login(started_game.master.user)
        character = started_game.player_set.first().character
        response = client.post(
            reverse(self.path_name, args=(started_game.id,)),
            data={"character_id": character.id, "skill": "Perception"},
        )
        assert response.status_code == 200
        # Should contain a roll result (number)
        content = response.content.decode()
        assert "Perception" in content

    def test_roll_insight(self, client, started_game):
        client.force_login(started_game.master.user)
        character = started_game.player_set.first().character
        response = client.post(
            reverse(self.path_name, args=(started_game.id,)),
            data={"character_id": character.id, "skill": "Insight"},
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "Insight" in content
```

**Step 2: Run test to verify it fails**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMSecretRollsPanelView -v`

Expected: FAIL with "NoReverseMatch: Reverse for 'dm-secret-rolls' not found"

**Step 3: Add Secret Rolls views**

Add to `game/views/dm_dashboard.py`:

```python
import random

from character.constants.skills import SkillName


class DMSecretRollsPanelView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """HTMX partial for secret rolls panel."""

    def test_func(self):
        return self.is_user_master()

    def get(self, request, *args, **kwargs):
        characters = Character.objects.filter(player__game=self.game)

        context = {
            "game": self.game,
            "characters": characters,
        }
        html = render_to_string("game/partials/dm_secret_rolls.html", context, request)
        return HttpResponse(html)


class DMSecretRollView(
    LoginRequiredMixin, UserPassesTestMixin, GameContextMixin, View
):
    """Execute a secret skill roll."""

    def test_func(self):
        return self.is_user_master()

    def post(self, request, *args, **kwargs):
        character_id = request.POST.get("character_id")
        skill_name = request.POST.get("skill")

        character = Character.objects.get(
            id=character_id, player__game=self.game
        )

        # Get wisdom modifier (both Perception and Insight use WIS)
        wisdom_mod = character.wisdom.modifier

        # Check if character is proficient in this skill
        is_proficient = character.skills.filter(name=skill_name).exists()
        prof_bonus = character.proficiency_bonus if is_proficient else 0

        # Roll d20
        d20_roll = random.randint(1, 20)
        total = d20_roll + wisdom_mod + prof_bonus

        # Build modifier string
        mod_parts = []
        if wisdom_mod != 0:
            mod_parts.append(f"{wisdom_mod:+d} WIS")
        if prof_bonus > 0:
            mod_parts.append(f"+{prof_bonus} prof")
        mod_str = ", ".join(mod_parts) if mod_parts else "+0"

        result_html = f"""
        <div class="roll-result">
            <span class="roll-char">{character.name}</span>
            <span class="roll-skill">{skill_name}:</span>
            <span class="roll-total">{total}</span>
            <span class="roll-detail">(d20:{d20_roll} {mod_str})</span>
        </div>
        """

        return HttpResponse(result_html)
```

**Step 4: Add URL patterns**

Add to `game/urls.py`:

```python
    path(
        "<int:game_id>/dm/secret-rolls/",
        dm_dashboard.DMSecretRollsPanelView.as_view(),
        name="dm-secret-rolls",
    ),
    path(
        "<int:game_id>/dm/secret-rolls/roll/",
        dm_dashboard.DMSecretRollView.as_view(),
        name="dm-secret-roll",
    ),
```

**Step 5: Create secret rolls panel template**

Create `game/templates/game/partials/dm_secret_rolls.html`:

```html
<div class="secret-rolls-panel">
    <div class="roll-controls">
        <select id="secret-roll-character" class="character-select">
            {% for character in characters %}
            <option value="{{ character.id }}">{{ character.name }}</option>
            {% endfor %}
        </select>

        <div class="roll-buttons">
            <button class="rpg-btn btn-skill"
                    hx-post="{% url 'dm-secret-roll' game.id %}"
                    hx-vals='js:{character_id: document.getElementById("secret-roll-character").value, skill: "Perception"}'
                    hx-target="#secret-roll-log"
                    hx-swap="afterbegin">
                Perception
            </button>
            <button class="rpg-btn btn-skill"
                    hx-post="{% url 'dm-secret-roll' game.id %}"
                    hx-vals='js:{character_id: document.getElementById("secret-roll-character").value, skill: "Insight"}'
                    hx-target="#secret-roll-log"
                    hx-swap="afterbegin">
                Insight
            </button>
        </div>
    </div>

    <div id="secret-roll-log" class="roll-log">
        <p class="text-muted">Secret roll results appear here...</p>
    </div>
</div>

<style>
.secret-rolls-panel {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.roll-controls {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.character-select {
    width: 100%;
    padding: 8px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    color: var(--color-text);
    font-size: 1rem;
}

.roll-buttons {
    display: flex;
    gap: 10px;
}

.roll-buttons .rpg-btn {
    flex: 1;
}

.roll-log {
    flex: 1;
    min-height: 150px;
    max-height: 250px;
    overflow-y: auto;
    padding: 10px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--color-border);
    border-radius: 4px;
}

.roll-result {
    padding: 6px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 0.9rem;
}

.roll-char {
    font-weight: 600;
    color: var(--color-primary);
}

.roll-skill {
    color: var(--color-text-muted);
    margin-left: 5px;
}

.roll-total {
    font-weight: bold;
    font-size: 1.1rem;
    margin-left: 5px;
}

.roll-detail {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    margin-left: 5px;
}
</style>
```

**Step 6: Run test to verify it passes**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py::TestDMSecretRollsPanelView game/tests/views/test_dm_dashboard.py::TestDMSecretRollView -v`

Expected: PASS

**Step 7: Commit**

```bash
git add game/views/dm_dashboard.py game/urls.py game/templates/game/partials/dm_secret_rolls.html game/tests/views/test_dm_dashboard.py
git commit -m "$(cat <<'EOF'
feat(game): add secret rolls panel for DM dashboard

DM can roll Perception and Insight checks secretly for any character.
Results shown only to DM, not broadcast to players.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Add Dashboard Link to Game View

**Files:**
- Modify: `game/templates/game/game.html`
- Test: Manual verification

**Step 1: Add link to Master's Panel**

In `game/templates/game/game.html`, find the Master's Panel section (around line 103-118) and add a dashboard link.

After line 106 (`<h3 class="panel-title"...>`), add:

```html
                                <div class="action-buttons" style="flex-direction: column;">
                                    <a href="{% url 'dm-dashboard' game.id %}" class="rpg-btn btn-secondary" target="_blank">
                                        Open DM Dashboard
                                    </a>
```

And update the existing `<div class="action-buttons"...>` to remove duplication.

**Step 2: Verify manually**

Run: `doppler run -- uv run poe dev-run`

Navigate to a game where you're the master and verify the "Open DM Dashboard" button appears and works.

**Step 3: Commit**

```bash
git add game/templates/game/game.html
git commit -m "$(cat <<'EOF'
feat(game): add DM dashboard link to game view

Adds "Open DM Dashboard" button in Master's Panel, opens in new tab.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: Run Full Test Suite and Pre-commit

**Step 1: Run all DM dashboard tests**

Run: `doppler run -- uv run poe test game/tests/views/test_dm_dashboard.py -v`

Expected: All tests PASS

**Step 2: Run full test suite**

Run: `doppler run -- uv run poe test`

Expected: All tests PASS

**Step 3: Run pre-commit checks**

Run: `pre-commit run --all-files`

Expected: All checks PASS

**Step 4: Fix any issues**

If any tests fail or pre-commit issues arise, fix them before proceeding.

**Step 5: Final commit if fixes needed**

```bash
git add -A
git commit -m "$(cat <<'EOF'
fix: address linting and test issues for DM dashboard

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Summary

This plan creates the DM Dashboard feature in 12 tasks:

1. **Character location field** - Foundation for party tracking
2. **SessionNote model** - Persistence for DM notes
3. **EncounterTemplate models** - Pre-built encounter storage
4. **Dashboard view + URL** - Main page structure
5. **Party overview panel** - HP, conditions, locations
6. **Initiative tracker panel** - Combat management
7. **Monster quick-add panel** - Search and select monsters
8. **Encounter manager panel** - Template CRUD
9. **Session notes panel** - Auto-saving textarea
10. **Secret rolls panel** - Perception/Insight checks
11. **Game view link** - Navigation from existing UI
12. **Full test suite** - Verification

Each task follows TDD with explicit test-first steps and commits.
