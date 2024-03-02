import pytest
from faker import Faker

from character.constants.character import Gender
from character.models.character import Character
from character.models.proficiencies import SavingThrowProficiency
from utils.dice import Dice

from ..factories import AbilityFactory, CharacterFactory


@pytest.mark.django_db
class TestCharacterModel:
    @pytest.fixture
    def character(self):
        return CharacterFactory(name="character", xp=0)

    def test_creation(self, character):
        isinstance(character, Character)
        assert character.level == 1
        assert character.xp == 0
        assert character.hp == 100
        assert character.proficiency_bonus == 2
        assert character.gender == Gender.MALE
        assert character.ac == 0

    def test_str(self, character):
        assert str(character) == character.name

    def test_xp_increase_no_level_increase(self, character):
        fake = Faker()
        new_xp = fake.random_int(max=200)
        old_xp = character.xp
        character.increase_xp(new_xp)
        assert character.xp == old_xp + new_xp

    def test_xp_increase_one_level_increase(self, character):
        fake = Faker()
        new_xp = fake.random_int(min=300, max=500)
        old_xp = character.xp
        old_level = character.level
        old_bonus = character.proficiency_bonus
        old_throws = Dice(character.hit_dice).throws
        old_max_hp = character.max_hp
        character.increase_xp(new_xp)
        assert character.xp == old_xp + new_xp
        assert character.level == old_level + 1
        assert character.proficiency_bonus == old_bonus + 2
        assert Dice(character.hit_dice).throws == old_throws + 1
        assert character.max_hp == old_max_hp + character.hp_increase

    def test_xp_increase_several_level_increase(self, character):
        new_xp = 50_000
        old_xp = character.xp
        old_throws = Dice(character.hit_dice).throws
        old_max_hp = character.max_hp
        character.increase_xp(new_xp)
        assert character.xp == old_xp + new_xp
        assert character.level == 9
        assert character.proficiency_bonus == 24
        assert Dice(character.hit_dice).throws == old_throws + 8
        assert character.max_hp == old_max_hp + character.hp_increase * 8

    def test_is_proficient_ability_present(self, character):
        ability = AbilityFactory(character=character)
        SavingThrowProficiency.objects.create(
            character=character, ability_type=ability.ability_type
        )
        assert character.is_proficient(ability)

    def test_is_proficient_ability_absent(self, character):
        ability = AbilityFactory(character=character)
        assert character.is_proficient(ability) is False
