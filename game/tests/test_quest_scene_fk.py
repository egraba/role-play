import pytest

from adventure.tests.factories import SceneFactory
from game.tests.factories import QuestFactory


@pytest.mark.django_db
def test_quest_can_reference_scene() -> None:
    scene = SceneFactory()
    quest = QuestFactory(scene=scene)
    assert quest.scene == scene


@pytest.mark.django_db
def test_quest_scene_is_optional() -> None:
    quest = QuestFactory()
    assert quest.scene is None
