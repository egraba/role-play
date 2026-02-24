import pytest

from adventure.tests.factories import (
    ActFactory,
    CampaignFactory,
    EncounterFactory,
    LocationFactory,
    NPCFactory,
    SceneFactory,
)
from user.tests.factories import UserFactory


@pytest.mark.django_db
def test_campaign_str():
    campaign = CampaignFactory(title="The Lost Mine")
    assert str(campaign) == "The Lost Mine"


@pytest.mark.django_db
def test_campaign_slug_auto_generated():
    campaign = CampaignFactory(title="The Lost Mine of Phandelver")
    assert campaign.slug == "the-lost-mine-of-phandelver"


@pytest.mark.django_db
def test_campaign_has_owner():
    user = UserFactory()
    campaign = CampaignFactory(owner=user)
    assert campaign.owner == user


@pytest.mark.django_db
@pytest.mark.skip(reason="URL config registered in Task 9")
def test_campaign_get_absolute_url():
    campaign = CampaignFactory(title="Test Campaign")
    assert campaign.get_absolute_url() == f"/adventure/{campaign.slug}/"


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
