import pytest
from django.urls import reverse

from adventure.models import Act, Encounter, Location, NPC, Scene
from adventure.tests.factories import (
    ActFactory,
    CampaignFactory,
    EncounterFactory,
    LocationFactory,
    NPCFactory,
    SceneFactory,
)
from user.tests.factories import UserFactory


# ---------------------------------------------------------------------------
# Act tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_act_create(client):
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    response = client.post(
        reverse("adventure:act-create", kwargs={"slug": campaign.slug}),
        {"title": "Act I", "order": 1, "summary": "", "goal": ""},
    )
    assert response.status_code == 302
    assert campaign.acts.filter(title="Act I").exists()


@pytest.mark.django_db
def test_act_create_non_owner_denied(client):
    user = UserFactory()
    campaign = CampaignFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse("adventure:act-create", kwargs={"slug": campaign.slug}),
        {"title": "Act I", "order": 1, "summary": "", "goal": ""},
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_act_detail_accessible_by_owner(client):
    user = UserFactory()
    act = ActFactory(campaign=CampaignFactory(owner=user))
    client.force_login(user)
    response = client.get(
        reverse(
            "adventure:act-detail", kwargs={"slug": act.campaign.slug, "pk": act.pk}
        )
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_act_detail_non_owner_denied(client):
    user = UserFactory()
    act = ActFactory()  # different owner
    client.force_login(user)
    response = client.get(
        reverse(
            "adventure:act-detail", kwargs={"slug": act.campaign.slug, "pk": act.pk}
        )
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_act_update_by_owner(client):
    user = UserFactory()
    act = ActFactory(campaign=CampaignFactory(owner=user))
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:act-update",
            kwargs={"slug": act.campaign.slug, "pk": act.pk},
        ),
        {"title": "Updated Act", "order": act.order, "summary": "", "goal": ""},
    )
    assert response.status_code == 302
    act.refresh_from_db()
    assert act.title == "Updated Act"


@pytest.mark.django_db
def test_act_update_non_owner_denied(client):
    user = UserFactory()
    act = ActFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:act-update",
            kwargs={"slug": act.campaign.slug, "pk": act.pk},
        ),
        {"title": "Hacked", "order": act.order, "summary": "", "goal": ""},
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_act_delete_by_owner(client):
    user = UserFactory()
    act = ActFactory(campaign=CampaignFactory(owner=user))
    pk = act.pk
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:act-delete",
            kwargs={"slug": act.campaign.slug, "pk": act.pk},
        )
    )
    assert response.status_code == 302
    assert not Act.objects.filter(pk=pk).exists()


@pytest.mark.django_db
def test_act_delete_non_owner_denied(client):
    user = UserFactory()
    act = ActFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:act-delete",
            kwargs={"slug": act.campaign.slug, "pk": act.pk},
        )
    )
    assert response.status_code == 404
    assert Act.objects.filter(pk=act.pk).exists()


# ---------------------------------------------------------------------------
# Scene tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_scene_create(client):
    user = UserFactory()
    act = ActFactory(campaign=CampaignFactory(owner=user))
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:scene-create",
            kwargs={"slug": act.campaign.slug, "act_pk": act.pk},
        ),
        {
            "title": "The Cave",
            "order": 1,
            "scene_type": "E",
            "description": "",
            "hook": "",
            "resolution": "",
        },
    )
    assert response.status_code == 302
    assert act.scenes.filter(title="The Cave").exists()


@pytest.mark.django_db
def test_scene_create_non_owner_denied(client):
    user = UserFactory()
    act = ActFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:scene-create",
            kwargs={"slug": act.campaign.slug, "act_pk": act.pk},
        ),
        {
            "title": "The Cave",
            "order": 1,
            "scene_type": "E",
            "description": "",
            "hook": "",
            "resolution": "",
        },
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_scene_detail_accessible_by_owner(client):
    user = UserFactory()
    scene = SceneFactory(act=ActFactory(campaign=CampaignFactory(owner=user)))
    client.force_login(user)
    response = client.get(
        reverse(
            "adventure:scene-detail",
            kwargs={
                "slug": scene.act.campaign.slug,
                "act_pk": scene.act.pk,
                "pk": scene.pk,
            },
        )
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_scene_detail_non_owner_denied(client):
    user = UserFactory()
    scene = SceneFactory()  # different owner
    client.force_login(user)
    response = client.get(
        reverse(
            "adventure:scene-detail",
            kwargs={
                "slug": scene.act.campaign.slug,
                "act_pk": scene.act.pk,
                "pk": scene.pk,
            },
        )
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_scene_delete_by_owner(client):
    user = UserFactory()
    scene = SceneFactory(act=ActFactory(campaign=CampaignFactory(owner=user)))
    pk = scene.pk
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:scene-delete",
            kwargs={
                "slug": scene.act.campaign.slug,
                "act_pk": scene.act.pk,
                "pk": scene.pk,
            },
        )
    )
    assert response.status_code == 302
    assert not Scene.objects.filter(pk=pk).exists()


@pytest.mark.django_db
def test_scene_delete_non_owner_denied(client):
    user = UserFactory()
    scene = SceneFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:scene-delete",
            kwargs={
                "slug": scene.act.campaign.slug,
                "act_pk": scene.act.pk,
                "pk": scene.pk,
            },
        )
    )
    assert response.status_code == 404
    assert Scene.objects.filter(pk=scene.pk).exists()


# ---------------------------------------------------------------------------
# NPC tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_npc_create(client):
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    response = client.post(
        reverse("adventure:npc-create", kwargs={"slug": campaign.slug}),
        {
            "name": "Gandalf",
            "role": "wizard",
            "motivation": "",
            "personality": "",
            "appearance": "",
            "notes": "",
        },
    )
    assert response.status_code == 302
    assert campaign.npcs.filter(name="Gandalf").exists()


@pytest.mark.django_db
def test_npc_create_non_owner_denied(client):
    user = UserFactory()
    campaign = CampaignFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse("adventure:npc-create", kwargs={"slug": campaign.slug}),
        {
            "name": "Gandalf",
            "role": "wizard",
            "motivation": "",
            "personality": "",
            "appearance": "",
            "notes": "",
        },
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_npc_update_by_owner(client):
    user = UserFactory()
    npc = NPCFactory(campaign=CampaignFactory(owner=user))
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:npc-update",
            kwargs={"slug": npc.campaign.slug, "pk": npc.pk},
        ),
        {
            "name": "Updated Name",
            "role": npc.role,
            "motivation": "",
            "personality": "",
            "appearance": "",
            "notes": "",
        },
    )
    assert response.status_code == 302
    npc.refresh_from_db()
    assert npc.name == "Updated Name"


@pytest.mark.django_db
def test_npc_update_non_owner_denied(client):
    user = UserFactory()
    npc = NPCFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:npc-update",
            kwargs={"slug": npc.campaign.slug, "pk": npc.pk},
        ),
        {
            "name": "Hacked",
            "role": "",
            "motivation": "",
            "personality": "",
            "appearance": "",
            "notes": "",
        },
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_npc_delete_by_owner(client):
    user = UserFactory()
    npc = NPCFactory(campaign=CampaignFactory(owner=user))
    pk = npc.pk
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:npc-delete",
            kwargs={"slug": npc.campaign.slug, "pk": npc.pk},
        )
    )
    assert response.status_code == 302
    assert not NPC.objects.filter(pk=pk).exists()


@pytest.mark.django_db
def test_npc_delete_non_owner_denied(client):
    user = UserFactory()
    npc = NPCFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:npc-delete",
            kwargs={"slug": npc.campaign.slug, "pk": npc.pk},
        )
    )
    assert response.status_code == 404
    assert NPC.objects.filter(pk=npc.pk).exists()


# ---------------------------------------------------------------------------
# Location tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_location_create(client):
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    client.force_login(user)
    response = client.post(
        reverse("adventure:location-create", kwargs={"slug": campaign.slug}),
        {"name": "The Dungeon", "description": "", "region": "dungeon"},
    )
    assert response.status_code == 302
    assert campaign.locations.filter(name="The Dungeon").exists()


@pytest.mark.django_db
def test_location_create_non_owner_denied(client):
    user = UserFactory()
    campaign = CampaignFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse("adventure:location-create", kwargs={"slug": campaign.slug}),
        {"name": "The Dungeon", "description": "", "region": "dungeon"},
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_location_update_by_owner(client):
    user = UserFactory()
    location = LocationFactory(campaign=CampaignFactory(owner=user))
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:location-update",
            kwargs={"slug": location.campaign.slug, "pk": location.pk},
        ),
        {"name": "Updated Place", "description": "", "region": "dungeon"},
    )
    assert response.status_code == 302
    location.refresh_from_db()
    assert location.name == "Updated Place"


@pytest.mark.django_db
def test_location_update_non_owner_denied(client):
    user = UserFactory()
    location = LocationFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:location-update",
            kwargs={"slug": location.campaign.slug, "pk": location.pk},
        ),
        {"name": "Hacked Place", "description": "", "region": "dungeon"},
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_location_delete_by_owner(client):
    user = UserFactory()
    location = LocationFactory(campaign=CampaignFactory(owner=user))
    pk = location.pk
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:location-delete",
            kwargs={"slug": location.campaign.slug, "pk": location.pk},
        )
    )
    assert response.status_code == 302
    assert not Location.objects.filter(pk=pk).exists()


@pytest.mark.django_db
def test_location_delete_non_owner_denied(client):
    user = UserFactory()
    location = LocationFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:location-delete",
            kwargs={"slug": location.campaign.slug, "pk": location.pk},
        )
    )
    assert response.status_code == 404
    assert Location.objects.filter(pk=location.pk).exists()


# ---------------------------------------------------------------------------
# Encounter tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_encounter_create(client):
    user = UserFactory()
    scene = SceneFactory(act=ActFactory(campaign=CampaignFactory(owner=user)))
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:encounter-create",
            kwargs={
                "slug": scene.act.campaign.slug,
                "act_pk": scene.act.pk,
                "scene_pk": scene.pk,
            },
        ),
        {
            "title": "Goblin Ambush",
            "order": 1,
            "encounter_type": "C",
            "description": "",
            "difficulty": "M",
            "rewards": "",
        },
    )
    assert response.status_code == 302
    assert scene.encounters.filter(title="Goblin Ambush").exists()


@pytest.mark.django_db
def test_encounter_create_non_owner_denied(client):
    user = UserFactory()
    scene = SceneFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:encounter-create",
            kwargs={
                "slug": scene.act.campaign.slug,
                "act_pk": scene.act.pk,
                "scene_pk": scene.pk,
            },
        ),
        {
            "title": "Goblin Ambush",
            "order": 1,
            "encounter_type": "C",
            "description": "",
            "difficulty": "M",
            "rewards": "",
        },
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_encounter_delete_by_owner(client):
    user = UserFactory()
    encounter = EncounterFactory(
        scene=SceneFactory(act=ActFactory(campaign=CampaignFactory(owner=user)))
    )
    pk = encounter.pk
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:encounter-delete",
            kwargs={
                "slug": encounter.scene.act.campaign.slug,
                "act_pk": encounter.scene.act.pk,
                "scene_pk": encounter.scene.pk,
                "pk": encounter.pk,
            },
        )
    )
    assert response.status_code == 302
    assert not Encounter.objects.filter(pk=pk).exists()


@pytest.mark.django_db
def test_encounter_delete_non_owner_denied(client):
    user = UserFactory()
    encounter = EncounterFactory()  # different owner
    client.force_login(user)
    response = client.post(
        reverse(
            "adventure:encounter-delete",
            kwargs={
                "slug": encounter.scene.act.campaign.slug,
                "act_pk": encounter.scene.act.pk,
                "scene_pk": encounter.scene.pk,
                "pk": encounter.pk,
            },
        )
    )
    assert response.status_code == 404
    assert Encounter.objects.filter(pk=encounter.pk).exists()
