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
