# Adventure App Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the `master/` app with a new `adventure/` app implementing the full SRD 5.2.1 pre-game planning hierarchy: Campaign → Act → Scene → Encounter, with NPC, Location, and BYOK AI generation at every level.

**Architecture:** New `adventure/` Django app with 7 models (Campaign, Act, Scene, Encounter, EncounterMonster, NPC, Location). `master.Campaign` data is migrated to `adventure.Campaign` and `master/` is deleted. `game.Game.campaign` FK is re-pointed; `game.Quest` gains a nullable `scene` FK.

**Tech Stack:** Python 3.14, Django 6.0, PostgreSQL, HTMX, factory_boy, pytest-django, Anthropic SDK (existing `ai/` app pattern)

**Design doc:** `docs/plans/2026-02-23-adventure-app-design.md`

---

## Conventions

- Run tests with: `doppler run -- uv run poe test`
- Run a single test: `doppler run -- uv run poe test -- tests/path/test.py::test_name -v`
- Lint/format before every commit: `pre-commit run --all-files`
- Commit message format: `feat:`, `fix:`, `test:`, `refactor:`, `docs:`
- All model fields need type hints on methods/properties
- Imports: stdlib → third-party → project (alphabetical within groups)
- Relative imports inside an app, absolute across apps

---

## Task 1: App skeleton

**Files:**
- Create: `adventure/__init__.py`
- Create: `adventure/apps.py`
- Modify: `role_play/settings/base.py` (INSTALLED_APPS)

**Step 1: Create the app init**

```python
# adventure/__init__.py
# (empty)
```

**Step 2: Create apps.py**

```python
# adventure/apps.py
from django.apps import AppConfig


class AdventureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "adventure"
```

**Step 3: Register in INSTALLED_APPS**

In `role_play/settings/base.py`, replace:
```python
"master.apps.MasterConfig",
```
with:
```python
"master.apps.MasterConfig",
"adventure.apps.AdventureConfig",
```
(Keep master for now — it is removed in Task 10.)

**Step 4: Verify Django can start**

```bash
doppler run -- uv run python manage.py check
```
Expected: `System check identified no issues (0 silenced).`

**Step 5: Commit**

```bash
git add adventure/ role_play/settings/base.py
git commit -m "feat: scaffold adventure app"
```

---

## Task 2: Constants

**Files:**
- Create: `adventure/constants.py`

**Step 1: Write the constants**

```python
# adventure/constants.py
from django.db import models


class SceneType(models.TextChoices):
    COMBAT = "C", "Combat"
    SOCIAL = "S", "Social Interaction"
    EXPLORATION = "E", "Exploration"
    REST = "R", "Rest"
    TRANSITION = "T", "Transition"


class EncounterType(models.TextChoices):
    COMBAT = "C", "Combat"
    SOCIAL = "S", "Social"
    TRAP = "T", "Trap"
    PUZZLE = "P", "Puzzle"
    EXPLORATION = "E", "Exploration"


class Difficulty(models.TextChoices):
    EASY = "E", "Easy"
    MEDIUM = "M", "Medium"
    HARD = "H", "Hard"
    DEADLY = "D", "Deadly"


class Tone(models.TextChoices):
    HEROIC = "heroic", "Heroic"
    DARK = "dark", "Dark"
    COMEDIC = "comedic", "Comedic"
    MYSTERY = "mystery", "Mystery"
    HORROR = "horror", "Horror"


class Region(models.TextChoices):
    DUNGEON = "dungeon", "Dungeon"
    CITY = "city", "City"
    WILDERNESS = "wilderness", "Wilderness"
    SEA = "sea", "Sea"
    PLANAR = "planar", "Planar"
    UNDERDARK = "underdark", "Underdark"
```

**Step 2: Write a constants test**

```python
# adventure/tests/__init__.py
# (empty)

# adventure/tests/test_constants.py
from adventure.constants import Difficulty, EncounterType, SceneType


def test_scene_type_choices():
    assert SceneType.COMBAT == "C"
    assert SceneType.SOCIAL == "S"
    assert SceneType.EXPLORATION == "E"


def test_difficulty_choices():
    assert Difficulty.EASY == "E"
    assert Difficulty.DEADLY == "D"


def test_encounter_type_choices():
    assert EncounterType.COMBAT == "C"
    assert EncounterType.TRAP == "T"
```

**Step 3: Run test**

```bash
doppler run -- uv run poe test -- adventure/tests/test_constants.py -v
```
Expected: 3 passed

**Step 4: Commit**

```bash
git add adventure/constants.py adventure/tests/
git commit -m "feat: add adventure constants (SceneType, Difficulty, etc.)"
```

---

## Task 3: Campaign model

**Files:**
- Create: `adventure/models.py`
- Create: `adventure/tests/factories.py`
- Create: `adventure/tests/test_models.py`

**Step 1: Write the failing model test**

```python
# adventure/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model

from adventure.tests.factories import CampaignFactory

User = get_user_model()


@pytest.mark.django_db
def test_campaign_str():
    campaign = CampaignFactory(title="The Lost Mine")
    assert str(campaign) == "The Lost Mine"


@pytest.mark.django_db
def test_campaign_slug_auto_generated():
    campaign = CampaignFactory(title="The Lost Mine of Phandelver")
    assert campaign.slug == "the-lost-mine-of-phandelver"


@pytest.mark.django_db
def test_campaign_has_owner(user):
    campaign = CampaignFactory(owner=user)
    assert campaign.owner == user


@pytest.mark.django_db
def test_campaign_get_absolute_url():
    campaign = CampaignFactory(title="Test Campaign")
    assert campaign.get_absolute_url() == f"/adventure/{campaign.slug}/"
```

**Step 2: Run test — verify it fails**

```bash
doppler run -- uv run poe test -- adventure/tests/test_models.py -v
```
Expected: ImportError (Campaign not defined yet)

**Step 3: Write the Campaign model**

```python
# adventure/models.py
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .constants import Difficulty, EncounterType, Region, SceneType, Tone


class Campaign(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    synopsis = models.TextField(max_length=3000, blank=True)
    main_conflict = models.TextField(max_length=1000, blank=True)
    objective = models.TextField(max_length=500, blank=True)
    party_level = models.SmallIntegerField(default=1)
    tone = models.CharField(
        max_length=10, choices=Tone, default=Tone.HEROIC
    )
    setting = models.TextField(max_length=1000, blank=True)

    def __str__(self) -> str:
        return str(self.title)

    def get_absolute_url(self) -> str:
        return reverse("adventure:campaign-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
```

**Step 4: Write the factory**

```python
# adventure/tests/factories.py
import factory
from django.contrib.auth import get_user_model

from adventure.models import Campaign

User = get_user_model()


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign
        django_get_or_create = ("title",)

    title = factory.Sequence(lambda n: f"campaign{n}")
    synopsis = factory.Faker("paragraph", nb_sentences=5)
    owner = factory.SubFactory("user.tests.factories.UserFactory")
```

Note: `user.tests.factories.UserFactory` already exists — check `user/tests/factories.py` for the exact import path. If it lives elsewhere, adjust the string.

**Step 5: Create and run the migration**

```bash
doppler run -- uv run python manage.py makemigrations adventure
```
Expected: `adventure/migrations/0001_initial.py` created

**Step 6: Apply migration**

```bash
doppler run -- uv run poe db-migrate
```

**Step 7: Run the model tests**

```bash
doppler run -- uv run poe test -- adventure/tests/test_models.py -v
```
Expected: 4 passed

**Step 8: Commit**

```bash
pre-commit run --all-files
git add adventure/
git commit -m "feat: add Campaign model with owner, party_level, tone, setting"
```

---

## Task 4: Act, Scene, NPC, Location models

**Files:**
- Modify: `adventure/models.py`
- Modify: `adventure/tests/factories.py`
- Modify: `adventure/tests/test_models.py`

**Step 1: Write failing tests**

Add to `adventure/tests/test_models.py`:

```python
from adventure.tests.factories import ActFactory, LocationFactory, NPCFactory, SceneFactory


@pytest.mark.django_db
def test_act_str():
    act = ActFactory(title="The Dark Descent")
    assert str(act) == "The Dark Descent"


@pytest.mark.django_db
def test_act_order_default():
    act = ActFactory()
    assert act.order >= 1


@pytest.mark.django_db
def test_scene_str():
    scene = SceneFactory(title="Ambush at the Bridge")
    assert str(scene) == "Ambush at the Bridge"


@pytest.mark.django_db
def test_scene_type_default_is_exploration():
    scene = SceneFactory()
    assert scene.scene_type == "E"


@pytest.mark.django_db
def test_npc_str():
    npc = NPCFactory(name="Gundren Rockseeker")
    assert str(npc) == "Gundren Rockseeker"


@pytest.mark.django_db
def test_location_str():
    loc = LocationFactory(name="Cragmaw Hideout")
    assert str(loc) == "Cragmaw Hideout"
```

**Step 2: Run — verify fails**

```bash
doppler run -- uv run poe test -- adventure/tests/test_models.py -v
```
Expected: ImportError

**Step 3: Add models to adventure/models.py**

Append after the `Campaign` class:

```python
class Act(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="acts"
    )
    title = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=1)
    summary = models.TextField(max_length=2000, blank=True)
    goal = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return str(self.title)


class Scene(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, related_name="scenes")
    title = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=1)
    scene_type = models.CharField(
        max_length=1, choices=SceneType, default=SceneType.EXPLORATION
    )
    description = models.TextField(max_length=3000, blank=True)
    hook = models.TextField(max_length=500, blank=True)
    resolution = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return str(self.title)


class NPC(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="npcs"
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, blank=True)
    motivation = models.TextField(max_length=500, blank=True)
    personality = models.TextField(max_length=500, blank=True)
    appearance = models.TextField(max_length=500, blank=True)
    stat_block = models.ForeignKey(
        "bestiary.MonsterSettings",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="npcs",
    )
    notes = models.TextField(max_length=1000, blank=True)

    def __str__(self) -> str:
        return str(self.name)


class Location(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="locations"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, blank=True)
    region = models.CharField(
        max_length=10, choices=Region, default=Region.DUNGEON
    )
    connections = models.ManyToManyField("self", blank=True)

    def __str__(self) -> str:
        return str(self.name)
```

**Step 4: Add factories**

Add to `adventure/tests/factories.py`:

```python
from adventure.models import Act, Location, NPC, Scene


class ActFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Act

    campaign = factory.SubFactory(CampaignFactory)
    title = factory.Sequence(lambda n: f"Act {n}")
    order = factory.Sequence(lambda n: n + 1)
    summary = factory.Faker("paragraph", nb_sentences=3)
    goal = factory.Faker("sentence")


class SceneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Scene

    act = factory.SubFactory(ActFactory)
    title = factory.Sequence(lambda n: f"Scene {n}")
    order = factory.Sequence(lambda n: n + 1)
    scene_type = "E"
    description = factory.Faker("paragraph", nb_sentences=3)
    hook = factory.Faker("sentence")
    resolution = factory.Faker("sentence")


class NPCFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NPC

    campaign = factory.SubFactory(CampaignFactory)
    name = factory.Sequence(lambda n: f"NPC {n}")
    role = "ally"
    motivation = factory.Faker("sentence")
    personality = factory.Faker("sentence")
    appearance = factory.Faker("sentence")


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    campaign = factory.SubFactory(CampaignFactory)
    name = factory.Sequence(lambda n: f"Location {n}")
    description = factory.Faker("paragraph", nb_sentences=2)
    region = "dungeon"
```

**Step 5: Run migration**

```bash
doppler run -- uv run python manage.py makemigrations adventure
doppler run -- uv run poe db-migrate
```

**Step 6: Run tests**

```bash
doppler run -- uv run poe test -- adventure/tests/test_models.py -v
```
Expected: all pass

**Step 7: Commit**

```bash
pre-commit run --all-files
git add adventure/
git commit -m "feat: add Act, Scene, NPC, Location models"
```

---

## Task 5: Encounter + EncounterMonster models

**Files:**
- Modify: `adventure/models.py`
- Modify: `adventure/tests/factories.py`
- Modify: `adventure/tests/test_models.py`

**Step 1: Write failing tests**

Add to `adventure/tests/test_models.py`:

```python
from adventure.tests.factories import EncounterFactory


@pytest.mark.django_db
def test_encounter_str():
    enc = EncounterFactory(title="Goblin Ambush")
    assert str(enc) == "Goblin Ambush"


@pytest.mark.django_db
def test_encounter_difficulty_default():
    enc = EncounterFactory()
    assert enc.difficulty == "M"


@pytest.mark.django_db
def test_encounter_belongs_to_scene():
    scene = SceneFactory()
    enc = EncounterFactory(scene=scene)
    assert enc.scene == scene
```

**Step 2: Add models to adventure/models.py**

```python
class Encounter(models.Model):
    scene = models.ForeignKey(
        Scene, on_delete=models.CASCADE, related_name="encounters"
    )
    title = models.CharField(max_length=100)
    encounter_type = models.CharField(
        max_length=1, choices=EncounterType, default=EncounterType.COMBAT
    )
    description = models.TextField(max_length=2000, blank=True)
    difficulty = models.CharField(
        max_length=1, choices=Difficulty, default=Difficulty.MEDIUM
    )
    monsters = models.ManyToManyField(
        "bestiary.MonsterSettings",
        through="EncounterMonster",
        blank=True,
        related_name="encounters",
    )
    npcs = models.ManyToManyField(NPC, blank=True, related_name="encounters")
    rewards = models.TextField(max_length=500, blank=True)

    def __str__(self) -> str:
        return str(self.title)


class EncounterMonster(models.Model):
    encounter = models.ForeignKey(
        Encounter, on_delete=models.CASCADE, related_name="encounter_monsters"
    )
    monster_settings = models.ForeignKey(
        "bestiary.MonsterSettings",
        on_delete=models.CASCADE,
        related_name="encounter_monsters",
    )
    count = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = [("encounter", "monster_settings")]
```

**Step 3: Add EncounterFactory**

```python
# In adventure/tests/factories.py
from adventure.models import Encounter


class EncounterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Encounter

    scene = factory.SubFactory(SceneFactory)
    title = factory.Sequence(lambda n: f"Encounter {n}")
    encounter_type = "C"
    difficulty = "M"
    description = factory.Faker("paragraph", nb_sentences=2)
```

**Step 4: Migrate and test**

```bash
doppler run -- uv run python manage.py makemigrations adventure
doppler run -- uv run poe db-migrate
doppler run -- uv run poe test -- adventure/tests/test_models.py -v
```
Expected: all pass

**Step 5: Commit**

```bash
pre-commit run --all-files
git add adventure/
git commit -m "feat: add Encounter and EncounterMonster models"
```

---

## Task 6: Data migration — master → adventure

**Files:**
- Create: `adventure/migrations/0002_migrate_from_master.py`

This migration copies all existing `master.Campaign` rows into `adventure.Campaign`. It runs before the master app is removed.

**Step 1: Write the data migration**

```python
# adventure/migrations/0002_migrate_from_master.py
from django.db import migrations


def copy_campaigns_forward(apps, schema_editor):
    MasterCampaign = apps.get_model("master", "Campaign")
    AdventureCampaign = apps.get_model("adventure", "Campaign")
    User = apps.get_model("auth", "User")

    # Use the first superuser as a placeholder owner for migrated campaigns.
    # Real campaigns should have owners assigned after migration.
    default_owner = User.objects.filter(is_superuser=True).first()
    if default_owner is None:
        default_owner = User.objects.first()
    if default_owner is None:
        return  # No users yet (fresh install) — nothing to migrate

    for master_campaign in MasterCampaign.objects.all():
        AdventureCampaign.objects.get_or_create(
            slug=master_campaign.slug,
            defaults={
                "title": master_campaign.title,
                "synopsis": master_campaign.synopsis,
                "main_conflict": master_campaign.main_conflict,
                "objective": master_campaign.objective,
                "owner": default_owner,
            },
        )


def copy_campaigns_backward(apps, schema_editor):
    # Reverse: remove adventure campaigns that were created from master
    AdventureCampaign = apps.get_model("adventure", "Campaign")
    MasterCampaign = apps.get_model("master", "Campaign")
    master_slugs = set(MasterCampaign.objects.values_list("slug", flat=True))
    AdventureCampaign.objects.filter(slug__in=master_slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("adventure", "0001_initial"),
        ("master", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(copy_campaigns_forward, copy_campaigns_backward),
    ]
```

**Step 2: Apply and verify**

```bash
doppler run -- uv run poe db-migrate
```

**Step 3: Smoke-test in Django shell**

```bash
doppler run -- uv run python manage.py shell -c "
from adventure.models import Campaign
from master.models import Campaign as MasterCampaign
print('master:', MasterCampaign.objects.count())
print('adventure:', Campaign.objects.count())
"
```
Expected: counts match (or adventure ≥ master if master is empty on dev).

**Step 4: Commit**

```bash
git add adventure/migrations/0002_migrate_from_master.py
git commit -m "feat: data migration — copy master.Campaign to adventure.Campaign"
```

---

## Task 7: Re-point game.Game.campaign FK

**Files:**
- Modify: `game/models/game.py`
- Create: `game/migrations/NNNN_update_campaign_fk.py` (auto-generated)
- Modify: `game/tests/` (update any tests that import from master)

**Step 1: Update game/models/game.py**

Change:
```python
from master.models import Campaign
```
to:
```python
from adventure.models import Campaign
```

The `campaign` field definition stays the same — only the import changes.

**Step 2: Write a failing test**

```python
# game/tests/test_campaign_fk.py
import pytest

from adventure.tests.factories import CampaignFactory
from game.tests.factories import GameFactory


@pytest.mark.django_db
def test_game_campaign_is_adventure_campaign():
    campaign = CampaignFactory()
    game = GameFactory(campaign=campaign)
    game.refresh_from_db()
    assert game.campaign == campaign
    assert game.campaign.__class__.__name__ == "Campaign"
    assert game.campaign.__module__.startswith("adventure")
```

**Step 3: Run — verify fails**

```bash
doppler run -- uv run poe test -- game/tests/test_campaign_fk.py -v
```
Expected: ImportError or model mismatch

**Step 4: Generate and apply the migration**

```bash
doppler run -- uv run python manage.py makemigrations game
doppler run -- uv run poe db-migrate
```

**Step 5: Run the test**

```bash
doppler run -- uv run poe test -- game/tests/test_campaign_fk.py -v
```
Expected: pass

**Step 6: Run full test suite — catch any master import breakage**

```bash
doppler run -- uv run poe test
```
Fix any remaining `from master.models import Campaign` imports in tests/views.

**Step 7: Commit**

```bash
pre-commit run --all-files
git add game/
git commit -m "feat: re-point game.Game.campaign FK to adventure.Campaign"
```

---

## Task 8: Add scene FK to game.Quest

**Files:**
- Modify: `game/models/game.py`
- Create migration (auto-generated)

**Step 1: Write failing test**

```python
# game/tests/test_quest_scene_fk.py
import pytest

from adventure.tests.factories import SceneFactory
from game.tests.factories import QuestFactory


@pytest.mark.django_db
def test_quest_can_reference_scene():
    scene = SceneFactory()
    quest = QuestFactory(scene=scene)
    quest.refresh_from_db()
    assert quest.scene == scene


@pytest.mark.django_db
def test_quest_scene_is_optional():
    quest = QuestFactory(scene=None)
    assert quest.scene is None
```

**Step 2: Update Quest model in game/models/game.py**

Add to the `Quest` class:
```python
scene = models.ForeignKey(
    "adventure.Scene",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="quests",
)
```

**Step 3: Check QuestFactory exists and supports scene=None**

Look in `game/tests/factories.py` — `QuestFactory` should set `scene=None` by default. If the factory doesn't exist yet, create it following the existing factory pattern in that file.

**Step 4: Migrate and test**

```bash
doppler run -- uv run python manage.py makemigrations game
doppler run -- uv run poe db-migrate
doppler run -- uv run poe test -- game/tests/test_quest_scene_fk.py -v
```
Expected: pass

**Step 5: Commit**

```bash
pre-commit run --all-files
git add game/
git commit -m "feat: add scene FK to game.Quest (links live game to pre-planned scene)"
```

---

## Task 9: Campaign CRUD views + URLs

**Files:**
- Create: `adventure/views.py`
- Create: `adventure/forms.py`
- Create: `adventure/urls.py`
- Create: `adventure/templates/adventure/campaign_list.html`
- Create: `adventure/templates/adventure/campaign_detail.html`
- Create: `adventure/templates/adventure/campaign_form.html`
- Modify: `role_play/urls.py`
- Create: `adventure/tests/test_views.py`

**Step 1: Write failing view tests**

```python
# adventure/tests/test_views.py
import pytest
from django.urls import reverse

from adventure.tests.factories import CampaignFactory


@pytest.mark.django_db
def test_campaign_list_requires_login(client):
    url = reverse("adventure:campaign-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
def test_campaign_list_shows_owned_campaigns(client, user):
    client.force_login(user)
    own = CampaignFactory(owner=user)
    other = CampaignFactory()  # different owner
    url = reverse("adventure:campaign-list")
    response = client.get(url)
    assert response.status_code == 200
    assert own.title in response.content.decode()
    assert other.title not in response.content.decode()


@pytest.mark.django_db
def test_campaign_create(client, user):
    client.force_login(user)
    url = reverse("adventure:campaign-create")
    response = client.post(
        url,
        {"title": "New Campaign", "party_level": 1, "tone": "heroic"},
    )
    assert response.status_code == 302
    from adventure.models import Campaign
    assert Campaign.objects.filter(title="New Campaign", owner=user).exists()


@pytest.mark.django_db
def test_campaign_detail(client, user):
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    url = reverse("adventure:campaign-detail", kwargs={"slug": campaign.slug})
    response = client.get(url)
    assert response.status_code == 200
    assert campaign.title in response.content.decode()


@pytest.mark.django_db
def test_campaign_detail_forbidden_for_non_owner(client, user):
    campaign = CampaignFactory()  # different owner
    client.force_login(user)
    url = reverse("adventure:campaign-detail", kwargs={"slug": campaign.slug})
    response = client.get(url)
    assert response.status_code == 403
```

**Step 2: Run — verify fails**

```bash
doppler run -- uv run poe test -- adventure/tests/test_views.py -v
```
Expected: NoReverseMatch or ImportError

**Step 3: Write views**

```python
# adventure/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CampaignForm
from .models import Campaign


class OwnerRequiredMixin(UserPassesTestMixin):
    """Restrict access to the campaign owner."""

    def test_func(self) -> bool:
        obj = self.get_object()
        return obj.owner == self.request.user


class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = "adventure/campaign_list.html"
    context_object_name = "campaigns"

    def get_queryset(self):
        return Campaign.objects.filter(owner=self.request.user).order_by("title")


class CampaignDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Campaign
    template_name = "adventure/campaign_detail.html"
    context_object_name = "campaign"


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "adventure/campaign_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CampaignUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "adventure/campaign_form.html"
```

**Step 4: Write forms**

```python
# adventure/forms.py
from django import forms

from .models import Act, Campaign, Encounter, Location, NPC, Scene


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["title", "synopsis", "main_conflict", "objective", "party_level", "tone", "setting"]
        widgets = {
            "synopsis": forms.Textarea(attrs={"rows": 6}),
            "main_conflict": forms.Textarea(attrs={"rows": 4}),
            "objective": forms.Textarea(attrs={"rows": 3}),
            "setting": forms.Textarea(attrs={"rows": 4}),
        }
```

**Step 5: Write URLs**

```python
# adventure/urls.py
from django.urls import path

from . import views

app_name = "adventure"

urlpatterns = [
    path("", views.CampaignListView.as_view(), name="campaign-list"),
    path("create/", views.CampaignCreateView.as_view(), name="campaign-create"),
    path("<slug:slug>/", views.CampaignDetailView.as_view(), name="campaign-detail"),
    path("<slug:slug>/edit/", views.CampaignUpdateView.as_view(), name="campaign-update"),
]
```

**Step 6: Register in root URLs**

In `role_play/urls.py`, add:
```python
path("adventure/", include("adventure.urls")),
```

**Step 7: Write minimal templates**

Create `adventure/templates/adventure/campaign_list.html`:
```html
{% extends 'base.html' %}
{% block content %}
<div class="rpg-container">
  <div class="rpg-panel">
    <h1 class="panel-title">My Campaigns</h1>
    <a href="{% url 'adventure:campaign-create' %}" class="rpg-btn btn-primary">New Campaign</a>
    {% for campaign in campaigns %}
    <div class="rpg-section">
      <a href="{{ campaign.get_absolute_url }}">{{ campaign.title }}</a>
      <span class="text-muted"> — Level {{ campaign.party_level }} {{ campaign.get_tone_display }}</span>
    </div>
    {% empty %}
    <p class="text-muted">No campaigns yet.</p>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

Create `adventure/templates/adventure/campaign_detail.html`:
```html
{% extends 'base.html' %}
{% block content %}
<div class="rpg-container">
  <div class="rpg-panel">
    <h1 class="panel-title">{{ campaign.title }}</h1>
    <p class="text-muted">Level {{ campaign.party_level }} &middot; {{ campaign.get_tone_display }}</p>
    <a href="{% url 'adventure:campaign-update' campaign.slug %}" class="rpg-btn btn-primary">Edit</a>

    <div class="rpg-section">
      <h2 class="panel-title" style="font-size:1.2rem">Acts</h2>
      {% for act in campaign.acts.all %}
      <div>Act {{ act.order }}: {{ act.title }}</div>
      {% empty %}
      <p class="text-muted">No acts yet.</p>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
```

Create `adventure/templates/adventure/campaign_form.html`:
```html
{% extends 'base.html' %}
{% block content %}
<div class="rpg-container">
  <div class="rpg-panel">
    <h1 class="panel-title">{% if object %}Edit Campaign{% else %}New Campaign{% endif %}</h1>
    <form method="post">
      {% csrf_token %}
      {% for field in form %}
      <div class="rpg-form-group">
        <label>{{ field.label }}</label>
        {{ field }}
        {% if field.errors %}<div class="text-danger">{{ field.errors }}</div>{% endif %}
      </div>
      {% endfor %}
      <button type="submit" class="rpg-btn btn-primary">Save</button>
      <a href="{% url 'adventure:campaign-list' %}" class="rpg-btn">Cancel</a>
    </form>
  </div>
</div>
{% endblock %}
```

**Step 8: Run tests**

```bash
doppler run -- uv run poe test -- adventure/tests/test_views.py -v
```
Expected: all pass

**Step 9: Commit**

```bash
pre-commit run --all-files
git add adventure/ role_play/urls.py
git commit -m "feat: Campaign CRUD views, forms, templates, URLs"
```

---

## Task 10: Act, Scene, NPC, Location, Encounter views

**Files:**
- Modify: `adventure/views.py`
- Modify: `adventure/forms.py`
- Modify: `adventure/urls.py`
- Create: templates for Act, Scene, NPC, Location, Encounter

**Step 1: Write failing tests**

Add to `adventure/tests/test_views.py`:

```python
from adventure.tests.factories import ActFactory, EncounterFactory, NPCFactory, SceneFactory


@pytest.mark.django_db
def test_act_create(client, user):
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    url = reverse("adventure:act-create", kwargs={"slug": campaign.slug})
    response = client.post(url, {"title": "Act One", "order": 1, "goal": "Reach the dungeon"})
    assert response.status_code == 302
    from adventure.models import Act
    assert Act.objects.filter(title="Act One", campaign=campaign).exists()


@pytest.mark.django_db
def test_scene_create(client, user):
    act = ActFactory(campaign=CampaignFactory(owner=user))
    client.force_login(user)
    url = reverse("adventure:scene-create", kwargs={"slug": act.campaign.slug, "act_id": act.id})
    response = client.post(url, {"title": "Scene One", "order": 1, "scene_type": "E"})
    assert response.status_code == 302
    from adventure.models import Scene
    assert Scene.objects.filter(title="Scene One", act=act).exists()


@pytest.mark.django_db
def test_npc_create(client, user):
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    url = reverse("adventure:npc-create", kwargs={"slug": campaign.slug})
    response = client.post(url, {"name": "Gundren", "role": "questgiver"})
    assert response.status_code == 302
    from adventure.models import NPC
    assert NPC.objects.filter(name="Gundren", campaign=campaign).exists()
```

**Step 2: Add views to adventure/views.py**

```python
from .models import Act, Encounter, EncounterMonster, Location, NPC, Scene


class ActDetailView(LoginRequiredMixin, DetailView):
    model = Act
    template_name = "adventure/act_detail.html"
    context_object_name = "act"

    def get_queryset(self):
        return Act.objects.filter(campaign__owner=self.request.user)


class ActCreateView(LoginRequiredMixin, CreateView):
    model = Act
    fields = ["title", "order", "summary", "goal"]
    template_name = "adventure/act_form.html"

    def get_campaign(self):
        return get_object_or_404(Campaign, slug=self.kwargs["slug"], owner=self.request.user)

    def form_valid(self, form):
        form.instance.campaign = self.get_campaign()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("adventure:campaign-detail", kwargs={"slug": self.kwargs["slug"]})


class ActUpdateView(LoginRequiredMixin, UpdateView):
    model = Act
    fields = ["title", "order", "summary", "goal"]
    template_name = "adventure/act_form.html"

    def get_queryset(self):
        return Act.objects.filter(campaign__owner=self.request.user)

    def get_success_url(self):
        return self.object.campaign.get_absolute_url()


class SceneDetailView(LoginRequiredMixin, DetailView):
    model = Scene
    template_name = "adventure/scene_detail.html"
    context_object_name = "scene"

    def get_queryset(self):
        return Scene.objects.filter(act__campaign__owner=self.request.user)


class SceneCreateView(LoginRequiredMixin, CreateView):
    model = Scene
    fields = ["title", "order", "scene_type", "description", "hook", "resolution"]
    template_name = "adventure/scene_form.html"

    def get_act(self):
        return get_object_or_404(
            Act, id=self.kwargs["act_id"], campaign__slug=self.kwargs["slug"], campaign__owner=self.request.user
        )

    def form_valid(self, form):
        form.instance.act = self.get_act()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "adventure:act-detail",
            kwargs={"slug": self.kwargs["slug"], "pk": self.kwargs["act_id"]},
        )


class SceneUpdateView(LoginRequiredMixin, UpdateView):
    model = Scene
    fields = ["title", "order", "scene_type", "description", "hook", "resolution"]
    template_name = "adventure/scene_form.html"

    def get_queryset(self):
        return Scene.objects.filter(act__campaign__owner=self.request.user)

    def get_success_url(self):
        act = self.object.act
        return reverse_lazy(
            "adventure:act-detail",
            kwargs={"slug": act.campaign.slug, "pk": act.pk},
        )


class NPCListView(LoginRequiredMixin, ListView):
    model = NPC
    template_name = "adventure/npc_list.html"
    context_object_name = "npcs"

    def get_queryset(self):
        return NPC.objects.filter(campaign__slug=self.kwargs["slug"], campaign__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["campaign"] = get_object_or_404(Campaign, slug=self.kwargs["slug"], owner=self.request.user)
        return ctx


class NPCCreateView(LoginRequiredMixin, CreateView):
    model = NPC
    fields = ["name", "role", "motivation", "personality", "appearance", "stat_block", "notes"]
    template_name = "adventure/npc_form.html"

    def get_campaign(self):
        return get_object_or_404(Campaign, slug=self.kwargs["slug"], owner=self.request.user)

    def form_valid(self, form):
        form.instance.campaign = self.get_campaign()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("adventure:npc-list", kwargs={"slug": self.kwargs["slug"]})


class NPCUpdateView(LoginRequiredMixin, UpdateView):
    model = NPC
    fields = ["name", "role", "motivation", "personality", "appearance", "stat_block", "notes"]
    template_name = "adventure/npc_form.html"

    def get_queryset(self):
        return NPC.objects.filter(campaign__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy("adventure:npc-list", kwargs={"slug": self.object.campaign.slug})


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "adventure/location_list.html"
    context_object_name = "locations"

    def get_queryset(self):
        return Location.objects.filter(campaign__slug=self.kwargs["slug"], campaign__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["campaign"] = get_object_or_404(Campaign, slug=self.kwargs["slug"], owner=self.request.user)
        return ctx


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    fields = ["name", "description", "region", "connections"]
    template_name = "adventure/location_form.html"

    def get_campaign(self):
        return get_object_or_404(Campaign, slug=self.kwargs["slug"], owner=self.request.user)

    def form_valid(self, form):
        form.instance.campaign = self.get_campaign()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("adventure:location-list", kwargs={"slug": self.kwargs["slug"]})


class EncounterCreateView(LoginRequiredMixin, CreateView):
    model = Encounter
    fields = ["title", "encounter_type", "description", "difficulty", "npcs", "rewards"]
    template_name = "adventure/encounter_form.html"

    def get_scene(self):
        return get_object_or_404(
            Scene, id=self.kwargs["scene_id"], act__campaign__owner=self.request.user
        )

    def form_valid(self, form):
        form.instance.scene = self.get_scene()
        return super().form_valid(form)

    def get_success_url(self):
        scene = self.object.scene
        return reverse_lazy("adventure:scene-detail", kwargs={"slug": scene.act.campaign.slug, "pk": scene.pk})


class EncounterUpdateView(LoginRequiredMixin, UpdateView):
    model = Encounter
    fields = ["title", "encounter_type", "description", "difficulty", "npcs", "rewards"]
    template_name = "adventure/encounter_form.html"

    def get_queryset(self):
        return Encounter.objects.filter(scene__act__campaign__owner=self.request.user)

    def get_success_url(self):
        scene = self.object.scene
        return reverse_lazy("adventure:scene-detail", kwargs={"slug": scene.act.campaign.slug, "pk": scene.pk})
```

Also add the missing import at the top of views.py:
```python
from django.shortcuts import get_object_or_404
```

**Step 3: Update URLs**

Replace the content of `adventure/urls.py` with:

```python
# adventure/urls.py
from django.urls import path

from . import views

app_name = "adventure"

urlpatterns = [
    # Campaign
    path("", views.CampaignListView.as_view(), name="campaign-list"),
    path("create/", views.CampaignCreateView.as_view(), name="campaign-create"),
    path("<slug:slug>/", views.CampaignDetailView.as_view(), name="campaign-detail"),
    path("<slug:slug>/edit/", views.CampaignUpdateView.as_view(), name="campaign-update"),
    # Acts
    path("<slug:slug>/acts/create/", views.ActCreateView.as_view(), name="act-create"),
    path("<slug:slug>/acts/<int:pk>/", views.ActDetailView.as_view(), name="act-detail"),
    path("<slug:slug>/acts/<int:pk>/edit/", views.ActUpdateView.as_view(), name="act-update"),
    # Scenes
    path("<slug:slug>/acts/<int:act_id>/scenes/create/", views.SceneCreateView.as_view(), name="scene-create"),
    path("<slug:slug>/scenes/<int:pk>/", views.SceneDetailView.as_view(), name="scene-detail"),
    path("<slug:slug>/scenes/<int:pk>/edit/", views.SceneUpdateView.as_view(), name="scene-update"),
    # Encounters
    path("<slug:slug>/scenes/<int:scene_id>/encounters/create/", views.EncounterCreateView.as_view(), name="encounter-create"),
    path("<slug:slug>/encounters/<int:pk>/edit/", views.EncounterUpdateView.as_view(), name="encounter-update"),
    # NPCs
    path("<slug:slug>/npcs/", views.NPCListView.as_view(), name="npc-list"),
    path("<slug:slug>/npcs/create/", views.NPCCreateView.as_view(), name="npc-create"),
    path("<slug:slug>/npcs/<int:pk>/edit/", views.NPCUpdateView.as_view(), name="npc-update"),
    # Locations
    path("<slug:slug>/locations/", views.LocationListView.as_view(), name="location-list"),
    path("<slug:slug>/locations/create/", views.LocationCreateView.as_view(), name="location-create"),
]
```

**Step 4: Create remaining templates** (minimal — styled with rpg-panel)

Create `adventure/templates/adventure/act_detail.html`:
```html
{% extends 'base.html' %}
{% block content %}
<div class="rpg-container">
  <div class="rpg-panel">
    <h1 class="panel-title">{{ act.title }}</h1>
    <p class="text-muted">{{ act.goal }}</p>
    <p>{{ act.summary }}</p>
    <a href="{% url 'adventure:scene-create' slug=act.campaign.slug act_id=act.id %}" class="rpg-btn btn-primary">Add Scene</a>
    {% for scene in act.scenes.all %}
    <div class="rpg-section">
      <span class="badge">{{ scene.get_scene_type_display }}</span>
      <a href="{% url 'adventure:scene-detail' slug=act.campaign.slug pk=scene.id %}">{{ scene.title }}</a>
    </div>
    {% empty %}
    <p class="text-muted">No scenes yet.</p>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

Create `adventure/templates/adventure/scene_detail.html`:
```html
{% extends 'base.html' %}
{% block content %}
<div class="rpg-container">
  <div class="rpg-panel">
    <h1 class="panel-title">{{ scene.title }}</h1>
    <span class="badge">{{ scene.get_scene_type_display }}</span>
    <div class="rpg-section">
      <h2 style="font-size:1.1rem">Hook</h2>
      <p>{{ scene.hook }}</p>
    </div>
    <div class="rpg-section">
      <h2 style="font-size:1.1rem">Description</h2>
      <p>{{ scene.description }}</p>
    </div>
    <div class="rpg-section">
      <h2 style="font-size:1.1rem">Resolution</h2>
      <p>{{ scene.resolution }}</p>
    </div>
    <div class="rpg-section">
      <h2 style="font-size:1.1rem">Encounters</h2>
      <a href="{% url 'adventure:encounter-create' slug=scene.act.campaign.slug scene_id=scene.id %}" class="rpg-btn btn-sm btn-primary">Add Encounter</a>
      {% for enc in scene.encounters.all %}
      <div>{{ enc.title }} — {{ enc.get_difficulty_display }}</div>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
```

Create minimal form templates for `act_form.html`, `scene_form.html`, `encounter_form.html`, `npc_form.html`, `npc_list.html`, `location_form.html`, `location_list.html` — all follow the same pattern as `campaign_form.html`. Just swap the title and form fields.

**Step 5: Run tests**

```bash
doppler run -- uv run poe test -- adventure/tests/test_views.py -v
```
Expected: all pass

**Step 6: Commit**

```bash
pre-commit run --all-files
git add adventure/
git commit -m "feat: Act, Scene, NPC, Location, Encounter CRUD views and templates"
```

---

## Task 11: AI generation service

**Files:**
- Create: `adventure/services/__init__.py`
- Create: `adventure/services/ai.py`
- Create: `adventure/tests/test_ai_service.py`

**Step 1: Write failing tests**

```python
# adventure/tests/test_ai_service.py
from unittest.mock import MagicMock, patch

import pytest

from adventure.services.ai import (
    AINotConfiguredError,
    generate_act_summary,
    generate_campaign_synopsis,
    generate_npc,
    generate_scene,
)


def test_generate_campaign_synopsis_raises_if_no_key():
    with patch("adventure.services.ai.settings") as mock_settings:
        mock_settings.ANTHROPIC_API_KEY = None
        with pytest.raises(AINotConfiguredError):
            generate_campaign_synopsis(title="Test", tone="heroic", setting="Forest", party_level=3)


def test_generate_campaign_synopsis_returns_text():
    mock_client = MagicMock()
    mock_client.messages.create.return_value.content = [MagicMock(text="A dark quest begins.")]
    with patch("adventure.services.ai._get_client", return_value=mock_client):
        result = generate_campaign_synopsis(title="Test", tone="heroic", setting="Forest", party_level=3)
    assert result == "A dark quest begins."


def test_generate_npc_returns_dict():
    mock_client = MagicMock()
    mock_client.messages.create.return_value.content = [
        MagicMock(text='{"motivation": "Power", "personality": "Cunning", "appearance": "Tall"}')
    ]
    with patch("adventure.services.ai._get_client", return_value=mock_client):
        result = generate_npc(name="Voldemort", role="villain", campaign_tone="dark")
    assert "motivation" in result
```

**Step 2: Run — verify fails**

```bash
doppler run -- uv run poe test -- adventure/tests/test_ai_service.py -v
```
Expected: ImportError

**Step 3: Write the AI service**

```python
# adventure/services/__init__.py
# (empty)

# adventure/services/ai.py
import json
import logging

import anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert Dungeon Master helping to design D&D 5e SRD adventures. "
    "Be evocative, concise, and follow SRD 5.2.1 conventions."
)


class AINotConfiguredError(Exception):
    """Raised when no Anthropic API key is configured."""


def _get_client() -> anthropic.Anthropic:
    api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
    if not api_key:
        raise AINotConfiguredError(
            "No ANTHROPIC_API_KEY configured. Set it in your environment to use AI features."
        )
    return anthropic.Anthropic(api_key=api_key)


def _ask(prompt: str, max_tokens: int = 1024) -> str:
    client = _get_client()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_campaign_synopsis(
    *, title: str, tone: str, setting: str, party_level: int
) -> str:
    prompt = (
        f"Write a compelling campaign synopsis (3-4 paragraphs) for a {tone} D&D 5e adventure titled '{title}'. "
        f"The party is level {party_level}. Setting: {setting}. "
        "Cover the background story, the main conflict, and the ultimate objective."
    )
    return _ask(prompt, max_tokens=800)


def generate_act_summary(
    *, act_title: str, act_goal: str, campaign_synopsis: str
) -> str:
    prompt = (
        f"Write a 2-paragraph summary for Act '{act_title}' of a D&D campaign.\n"
        f"Act goal: {act_goal}\n"
        f"Campaign synopsis: {campaign_synopsis}\n"
        "Describe what happens in this act and what challenges the players will face."
    )
    return _ask(prompt, max_tokens=400)


def generate_scene(
    *, scene_title: str, scene_type: str, act_summary: str
) -> dict:
    """Returns dict with keys: description, hook, resolution."""
    prompt = (
        f"Write content for a {scene_type} scene titled '{scene_title}'.\n"
        f"Act context: {act_summary}\n"
        "Return a JSON object with exactly these keys: description, hook, resolution. "
        "Each should be 2-3 sentences. Return only valid JSON, no markdown."
    )
    raw = _ask(prompt, max_tokens=500)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("AI returned non-JSON scene content, using raw text")
        return {"description": raw, "hook": "", "resolution": ""}


def generate_npc(*, name: str, role: str, campaign_tone: str) -> dict:
    """Returns dict with keys: motivation, personality, appearance."""
    prompt = (
        f"Create a D&D NPC named '{name}' who is a {role} in a {campaign_tone} campaign.\n"
        "Return a JSON object with exactly these keys: motivation, personality, appearance. "
        "Each should be 1-2 sentences. Return only valid JSON, no markdown."
    )
    raw = _ask(prompt, max_tokens=400)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("AI returned non-JSON NPC content, using raw text")
        return {"motivation": raw, "personality": "", "appearance": ""}


def generate_encounter_description(
    *, scene_description: str, encounter_type: str, difficulty: str, party_level: int
) -> str:
    prompt = (
        f"Write a description for a {difficulty} {encounter_type} encounter for a level {party_level} party.\n"
        f"Scene context: {scene_description}\n"
        "2-3 vivid sentences that set the scene and tension."
    )
    return _ask(prompt, max_tokens=300)
```

**Step 4: Run tests**

```bash
doppler run -- uv run poe test -- adventure/tests/test_ai_service.py -v
```
Expected: 3 passed

**Step 5: Commit**

```bash
pre-commit run --all-files
git add adventure/services/ adventure/tests/test_ai_service.py
git commit -m "feat: AI generation service (campaign, act, scene, NPC, encounter)"
```

---

## Task 12: AI HTMX endpoints

**Files:**
- Modify: `adventure/views.py`
- Modify: `adventure/urls.py`
- Create: `adventure/templates/adventure/partials/ai_draft_result.html`
- Create: `adventure/tests/test_ai_views.py`

**Step 1: Write failing tests**

```python
# adventure/tests/test_ai_views.py
from unittest.mock import patch

import pytest
from django.urls import reverse

from adventure.tests.factories import CampaignFactory, NPCFactory, SceneFactory


@pytest.mark.django_db
def test_ai_generate_synopsis_returns_partial(client, user):
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    with patch("adventure.views.generate_campaign_synopsis", return_value="Epic story"):
        response = client.post(
            reverse("adventure:ai-generate-synopsis", kwargs={"slug": campaign.slug})
        )
    assert response.status_code == 200
    assert b"Epic story" in response.content


@pytest.mark.django_db
def test_ai_generate_npc_returns_partial(client, user):
    npc = NPCFactory(campaign=CampaignFactory(owner=user))
    client.force_login(user)
    with patch("adventure.views.generate_npc", return_value={"motivation": "Revenge", "personality": "Cold", "appearance": "Scarred"}):
        response = client.post(
            reverse("adventure:ai-generate-npc", kwargs={"slug": npc.campaign.slug, "pk": npc.pk})
        )
    assert response.status_code == 200
    assert b"Revenge" in response.content


@pytest.mark.django_db
def test_ai_returns_error_when_not_configured(client, user):
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    from adventure.services.ai import AINotConfiguredError
    with patch("adventure.views.generate_campaign_synopsis", side_effect=AINotConfiguredError("No key")):
        response = client.post(
            reverse("adventure:ai-generate-synopsis", kwargs={"slug": campaign.slug})
        )
    assert response.status_code == 200
    assert b"No key" in response.content
```

**Step 2: Add AI views to adventure/views.py**

```python
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.views import View

from .services.ai import (
    AINotConfiguredError,
    generate_act_summary,
    generate_campaign_synopsis,
    generate_encounter_description,
    generate_npc,
    generate_scene,
)


class AIGenerateSynopsisView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        campaign = get_object_or_404(Campaign, slug=slug, owner=request.user)
        try:
            text = generate_campaign_synopsis(
                title=campaign.title,
                tone=campaign.tone,
                setting=campaign.setting,
                party_level=campaign.party_level,
            )
            return HttpResponse(render_to_string(
                "adventure/partials/ai_draft_result.html",
                {"text": text, "field": "synopsis"},
            ))
        except AINotConfiguredError as e:
            return HttpResponse(f'<p class="text-danger">{e}</p>')


class AIGenerateActView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, slug: str, pk: int) -> HttpResponse:
        act = get_object_or_404(Act, pk=pk, campaign__slug=slug, campaign__owner=request.user)
        try:
            text = generate_act_summary(
                act_title=act.title,
                act_goal=act.goal,
                campaign_synopsis=act.campaign.synopsis,
            )
            return HttpResponse(render_to_string(
                "adventure/partials/ai_draft_result.html",
                {"text": text, "field": "summary"},
            ))
        except AINotConfiguredError as e:
            return HttpResponse(f'<p class="text-danger">{e}</p>')


class AIGenerateSceneView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, slug: str, pk: int) -> HttpResponse:
        scene = get_object_or_404(Scene, pk=pk, act__campaign__slug=slug, act__campaign__owner=request.user)
        try:
            data = generate_scene(
                scene_title=scene.title,
                scene_type=scene.get_scene_type_display(),
                act_summary=scene.act.summary,
            )
            return HttpResponse(render_to_string(
                "adventure/partials/ai_draft_result.html",
                {"data": data, "multi_field": True},
            ))
        except AINotConfiguredError as e:
            return HttpResponse(f'<p class="text-danger">{e}</p>')


class AIGenerateNPCView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, slug: str, pk: int) -> HttpResponse:
        npc = get_object_or_404(NPC, pk=pk, campaign__slug=slug, campaign__owner=request.user)
        try:
            data = generate_npc(
                name=npc.name,
                role=npc.role,
                campaign_tone=npc.campaign.tone,
            )
            return HttpResponse(render_to_string(
                "adventure/partials/ai_draft_result.html",
                {"data": data, "multi_field": True},
            ))
        except AINotConfiguredError as e:
            return HttpResponse(f'<p class="text-danger">{e}</p>')
```

**Step 3: Add AI URLs to adventure/urls.py**

Add these lines to the `urlpatterns` list:

```python
# AI generation endpoints
path("<slug:slug>/ai/synopsis/", views.AIGenerateSynopsisView.as_view(), name="ai-generate-synopsis"),
path("<slug:slug>/acts/<int:pk>/ai/summary/", views.AIGenerateActView.as_view(), name="ai-generate-act"),
path("<slug:slug>/scenes/<int:pk>/ai/scene/", views.AIGenerateSceneView.as_view(), name="ai-generate-scene"),
path("<slug:slug>/npcs/<int:pk>/ai/npc/", views.AIGenerateNPCView.as_view(), name="ai-generate-npc"),
```

**Step 4: Create the partial template**

```html
<!-- adventure/templates/adventure/partials/ai_draft_result.html -->
{% if multi_field %}
  {% for key, value in data.items %}
  <div class="ai-draft-field" data-field="{{ key }}">
    <label class="text-muted" style="font-size:0.8rem;">AI draft — {{ key }}</label>
    <textarea class="rpg-textarea" name="{{ key }}" rows="3">{{ value }}</textarea>
  </div>
  {% endfor %}
{% else %}
  <div class="ai-draft-field" data-field="{{ field }}">
    <label class="text-muted" style="font-size:0.8rem;">AI draft</label>
    <textarea class="rpg-textarea" name="{{ field }}" rows="5">{{ text }}</textarea>
  </div>
{% endif %}
```

**Step 5: Run tests**

```bash
doppler run -- uv run poe test -- adventure/tests/test_ai_views.py -v
```
Expected: 3 passed

**Step 6: Commit**

```bash
pre-commit run --all-files
git add adventure/
git commit -m "feat: AI HTMX endpoints for campaign, act, scene, NPC generation"
```

---

## Task 13: Delete master/ app

**Files:**
- Modify: `role_play/settings/base.py` (remove master from INSTALLED_APPS)
- Modify: `role_play/urls.py` (remove master urls)
- Delete: entire `master/` directory

**Step 1: Run full test suite first as baseline**

```bash
doppler run -- uv run poe test
```
All tests must pass before deleting anything.

**Step 2: Remove master from settings**

In `role_play/settings/base.py`, remove:
```python
"master.apps.MasterConfig",
```

**Step 3: Remove master URLs**

In `role_play/urls.py`, remove:
```python
path("master/", include("master.urls")),
```

**Step 4: Search for any remaining master imports**

```bash
grep -r "from master" . --include="*.py" --exclude-dir=".venv"
grep -r "import master" . --include="*.py" --exclude-dir=".venv"
```

Fix any that appear. Common spots: `game/models/game.py` (already updated in Task 7), test files, admin.

**Step 5: Delete the master/ directory**

```bash
rm -rf master/
```

**Step 6: Create a squash migration to remove master tables**

```bash
doppler run -- uv run python manage.py makemigrations game --name="remove_master_campaign_fk_cleanup"
```

If Django doesn't auto-detect anything, the master tables will be cleaned up by deleting the app from INSTALLED_APPS (Django won't manage them anymore). For a clean DB, run:

```bash
doppler run -- uv run python manage.py migrate master zero
```
This rolls back master migrations, dropping the `master_campaign` table.

**Step 7: Run full test suite**

```bash
doppler run -- uv run poe test
```
Expected: all pass (no master references remain)

**Step 8: Commit**

```bash
pre-commit run --all-files
git add -A
git commit -m "feat: delete master/ app — replaced by adventure/"
```

---

## Task 14: Wire adventure into navigation

**Files:**
- Modify: existing nav template (check `base.html` for nav links)

**Step 1: Find the navigation template**

```bash
grep -r "campaign-list\|master/" templates/ --include="*.html" -l
```

**Step 2: Replace master campaign links with adventure links**

Replace any `{% url 'campaign-list' %}` → `{% url 'adventure:campaign-list' %}`
Replace any `{% url 'campaign-create' %}` → `{% url 'adventure:campaign-create' %}`

**Step 3: Add adventure link to base nav**

In `base.html`, add a nav link to `/adventure/` for logged-in users.

**Step 4: Run full test suite**

```bash
doppler run -- uv run poe test
pre-commit run --all-files
```

**Step 5: Commit**

```bash
git add templates/
git commit -m "feat: wire adventure app into navigation"
```

---

## Task 15: Final verification + PR

**Step 1: Run full test suite with coverage**

```bash
doppler run -- uv run poe test-cov
```
Aim for ≥ existing coverage. No regressions allowed.

**Step 2: Run pre-commit on all files**

```bash
pre-commit run --all-files
```
All checks must pass.

**Step 3: Update CHANGELOG.md**

Under `## Unreleased`, add:

```markdown
### Added
- `adventure/` app: full SRD 5.2.1 pre-game planning hierarchy (Campaign → Act → Scene → Encounter)
- Campaign model with owner, party_level, tone, and setting fields
- Act, Scene, NPC, Location, Encounter, and EncounterMonster models
- AI generation for campaign synopsis, act summaries, scenes, and NPCs (BYOK)
- Owner-scoped campaign access — campaigns are private to their creator

### Removed
- `master/` app — replaced by `adventure/`

### Changed
- `game.Game.campaign` FK now points to `adventure.Campaign`
- `game.Quest` gains a nullable `scene` FK for live game → pre-planned scene handoff
```

**Step 4: Open PR**

```bash
git push origin HEAD
gh pr create --title "feat: adventure app — replace master/ with SRD hierarchy" \
  --body "Replaces the thin master/ app with adventure/ implementing Campaign → Act → Scene → Encounter with BYOK AI generation. See docs/plans/2026-02-23-adventure-app-design.md."
```
