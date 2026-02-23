# Adventure App Design

**Date**: 2026-02-23
**Branch**: feat/adventure-app
**Status**: Approved

## Problem

The current `master/` app is a thin CRUD wrapper around a `Campaign` model with three free-text fields (`synopsis`, `main_conflict`, `objective`). It does not map to how D&D 5e adventures are actually structured, has no ownership model, and provides no tools for pre-game planning. The `Quest` model in `game/` is a single `environment: TextField` — equally unstructured.

A Dungeon Master filling out three text blobs cannot build a playable adventure.

## Solution

Replace `master/` with a new `adventure/` Django app implementing the full SRD 5.2.1 adventure hierarchy: **Campaign → Act → Scene → Encounter**, with supporting `NPC` and `Location` models. AI generation (via BYOK Anthropic API key) assists at every level.

---

## Data Model

### Campaign (moved from `master/`, enhanced)

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField(50) | unique |
| `slug` | SlugField(50) | unique, auto-generated |
| `owner` | FK → User | **new** — currently has no ownership |
| `synopsis` | TextField(3000) | keep |
| `main_conflict` | TextField(1000) | keep |
| `objective` | TextField(500) | keep |
| `party_level` | SmallIntegerField | **new** — drives CR recommendations |
| `tone` | CharField(20) | **new** — dark / heroic / comedic / mystery |
| `setting` | TextField(1000) | **new** — world context for AI prompts |

### Act

| Field | Type | Notes |
|-------|------|-------|
| `campaign` | FK → Campaign | cascade |
| `title` | CharField(100) | |
| `order` | PositiveSmallIntegerField | ordering within campaign |
| `summary` | TextField(2000) | |
| `goal` | TextField(500) | what must happen for this act to resolve |

### Scene (replaces `game.Quest`)

| Field | Type | Notes |
|-------|------|-------|
| `act` | FK → Act | cascade |
| `title` | CharField(100) | |
| `order` | PositiveSmallIntegerField | ordering within act |
| `scene_type` | CharField(1) | choices: combat / social / exploration / rest / transition |
| `description` | TextField(3000) | |
| `hook` | TextField(500) | how players enter this scene |
| `resolution` | TextField(500) | how the scene concludes |

### Encounter

| Field | Type | Notes |
|-------|------|-------|
| `scene` | FK → Scene | cascade |
| `title` | CharField(100) | |
| `encounter_type` | CharField(1) | choices: combat / social / trap / puzzle / exploration |
| `description` | TextField(2000) | |
| `difficulty` | CharField(1) | choices: easy / medium / hard / deadly |
| `monsters` | M2M → MonsterSettings (through EncounterMonster) | with count field |
| `npcs` | M2M → NPC | |
| `rewards` | TextField(500) | XP, treasure, story rewards |

#### EncounterMonster (through table)

| Field | Type |
|-------|------|
| `encounter` | FK → Encounter |
| `monster_settings` | FK → MonsterSettings |
| `count` | PositiveSmallIntegerField (default 1) |

### NPC

Belongs to a campaign; reusable across scenes.

| Field | Type | Notes |
|-------|------|-------|
| `campaign` | FK → Campaign | cascade |
| `name` | CharField(100) | |
| `role` | CharField(20) | villain / ally / neutral / shopkeeper / questgiver / etc. |
| `motivation` | TextField(500) | |
| `personality` | TextField(500) | |
| `appearance` | TextField(500) | |
| `stat_block` | FK → MonsterSettings | optional — reuse existing stat blocks |
| `notes` | TextField(1000) | DM private notes |

### Location

| Field | Type | Notes |
|-------|------|-------|
| `campaign` | FK → Campaign | cascade |
| `name` | CharField(100) | |
| `description` | TextField(2000) | |
| `region` | CharField(20) | dungeon / city / wilderness / sea / planar |
| `connections` | M2M → self | linked locations (undirected) |

### game.Quest (existing — extended)

Add a nullable FK so a live game session can be pinned to a pre-planned scene:

```python
scene = models.ForeignKey(
    "adventure.Scene",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
)
```

---

## AI Integration

All AI calls go through the existing `ai/` app. **BYOK**: if `ANTHROPIC_API_KEY` is not configured in the environment, AI buttons are hidden. No key = no cost, no broken UI.

### Generation matrix

| Model | Button label | Context sent to Claude | Fields populated |
|-------|-------------|----------------------|-----------------|
| Campaign | "Draft synopsis" | title, tone, setting, party_level | synopsis, main_conflict, objective |
| Act | "Draft act" | campaign synopsis + act title + goal | summary |
| Scene | "Draft scene" | act summary + scene_type + scene title | description, hook, resolution |
| NPC | "Generate NPC" | campaign tone + name + role | motivation, personality, appearance |
| Encounter | "Suggest encounter" | scene description + party_level + encounter_type | description, rewards; monster suggestions from existing MonsterSettings |

### Encounter AI constraint

The encounter generator does **not** hallucinate stat blocks. It queries `MonsterSettings` for creatures within the appropriate CR range (derived from `party_level` + `difficulty` using SRD XP thresholds), passes the candidates to Claude, and receives back a selection with narrative framing. No invented monsters.

### BYOK pattern

```python
# ai/services.py — existing pattern, no changes needed
# If settings.ANTHROPIC_API_KEY is None → raise AINotConfiguredError
# Adventure views catch AINotConfiguredError → return "Configure your API key" partial
```

Self-hosters pay their own API costs. A future hosted tier wraps the same views behind a subscription check without changing the AI layer.

---

## UX & URL Structure

### URLs

```
/adventure/                              Campaign list (owned by current user)
/adventure/create/                       Create campaign
/adventure/<slug>/                       Campaign detail — acts list
/adventure/<slug>/edit/                  Edit campaign metadata
/adventure/<slug>/acts/create/           Create act
/adventure/<slug>/acts/<id>/             Act detail — scenes list
/adventure/<slug>/acts/<id>/edit/        Edit act
/adventure/<slug>/acts/<id>/scenes/create/   Create scene
/adventure/<slug>/scenes/<id>/           Scene detail — encounters + NPCs
/adventure/<slug>/scenes/<id>/edit/      Edit scene
/adventure/<slug>/npcs/                  Campaign NPC roster
/adventure/<slug>/npcs/create/           Create NPC
/adventure/<slug>/npcs/<id>/edit/        Edit NPC
/adventure/<slug>/locations/             Campaign locations
/adventure/<slug>/locations/create/      Create location
/adventure/ai/<model>/generate/          AI generation endpoint (HTMX POST)
```

### Page layouts

Uses the existing `rpg-panel` / `rpg-btn` / `rpg-table` design system.

**Campaign detail** — acts displayed as numbered cards in order, drag-to-reorder. "Add Act" button at the bottom. Right sidebar: NPC roster + Locations as quick-access lists.

**Act detail** — scenes as a vertical timeline. Each scene card shows: type icon (sword / speech-bubble / compass / moon / arrow), title, hook preview, scene_type badge. "Add Scene" inline at the bottom.

**Scene detail** — two-column layout:
- Left: description + hook + resolution fields, each with an "AI Draft" button (HTMX, streams result into textarea)
- Right: encounters list + linked NPCs panel

**Encounter editor** — monster picker queries `MonsterSettings` filtered by CR range (auto-calculated from `party_level` + `difficulty` selection). Shows live difficulty rating as monsters are added (SRD 5.2.1 XP threshold math). "Suggest encounter" AI button fills description + pre-selects monsters.

**NPC editor** — single form with all fields + one "Generate NPC" button that populates all AI-generated fields at once from name + role.

### Master → live game handoff

On the `Game` detail page: "Load scene" button sets `Quest.scene` FK. The DM dashboard then surfaces the active scene's description and encounters as planning context during play.

---

## Migration Strategy

1. Create `adventure/` app with all new models
2. Write a data migration to copy `master.Campaign` rows into `adventure.Campaign`
3. Update `game.Game.campaign` FK to point to `adventure.Campaign`
4. Add `scene` FK to `game.Quest`
5. Delete `master/` app and its migration history (squash or drop)

---

## Files to Create

| File | Purpose |
|------|---------|
| `adventure/__init__.py` | App init |
| `adventure/apps.py` | AppConfig |
| `adventure/models.py` | Campaign, Act, Scene, Encounter, EncounterMonster, NPC, Location |
| `adventure/views.py` | CRUD views + AI generation endpoint |
| `adventure/forms.py` | ModelForms per model |
| `adventure/urls.py` | URL patterns |
| `adventure/admin.py` | Admin registration |
| `adventure/constants.py` | SceneType, EncounterType, Difficulty, Tone, Region enums |
| `adventure/services/ai.py` | AI generation service functions |
| `adventure/tests/factories.py` | Factory Boy factories |
| `adventure/tests/test_models.py` | Model tests |
| `adventure/tests/test_views.py` | View tests |
| `adventure/templates/adventure/campaign_list.html` | |
| `adventure/templates/adventure/campaign_detail.html` | |
| `adventure/templates/adventure/campaign_form.html` | |
| `adventure/templates/adventure/act_detail.html` | |
| `adventure/templates/adventure/act_form.html` | |
| `adventure/templates/adventure/scene_detail.html` | |
| `adventure/templates/adventure/scene_form.html` | |
| `adventure/templates/adventure/encounter_form.html` | |
| `adventure/templates/adventure/npc_form.html` | |
| `adventure/templates/adventure/location_form.html` | |
| `adventure/templates/adventure/partials/ai_draft_button.html` | Reusable AI button partial |

## Files to Modify

| File | Change |
|------|--------|
| `role_play/settings.py` | Add `adventure` to `INSTALLED_APPS`, remove `master` |
| `role_play/urls.py` | Replace `master/` routes with `adventure/` |
| `game/models/game.py` | Update `campaign` FK to `adventure.Campaign` |
| `game/models/events.py` | Update any Campaign imports |
| `game/models/__init__.py` | Update exports |

## Files to Delete

- `master/` app (entire directory, after data migration)

---

## SRD 5.2.1 Alignment

- **Three Pillars**: Scene `scene_type` maps directly to Combat, Social Interaction, and Exploration
- **Encounter difficulty**: Easy / Medium / Hard / Deadly thresholds per SRD XP tables
- **CR recommendations**: Party level → appropriate CR range per SRD encounter building rules
- **Three-Act structure**: The `Act` model formalises the setup / confrontation / resolution arc
- **NPC motivations**: First-class field, not an afterthought
