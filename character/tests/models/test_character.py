import pytest
from faker import Faker

from character.models.character import Character
from utils.dice import Dice
from utils.factories import CharacterFactory


@pytest.mark.django_db
class TestCharacterModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.character = CharacterFactory(name="character", xp=0)

    def test_creation(self):
        isinstance(self.character, Character)
        assert self.character.level == 1
        assert self.character.xp == 0
        assert self.character.hp == 100
        assert self.character.proficiency_bonus == 2
        assert self.character.strength == 0
        assert self.character.dexterity == 0
        assert self.character.constitution == 0
        assert self.character.intelligence == 0
        assert self.character.wisdom == 0
        assert self.character.charisma == 0
        assert self.character.gender == Character.Gender.MALE
        assert self.character.ac == 0

    def test_str(self):
        assert str(self.character) == self.character.name

    def test_xp_increase_no_level_increase(self):
        fake = Faker()
        new_xp = fake.random_int(max=200)
        old_xp = self.character.xp
        self.character.increase_xp(new_xp)
        assert self.character.xp == old_xp + new_xp

    def test_xp_increase_one_level_increase(self):
        fake = Faker()
        new_xp = fake.random_int(min=300, max=500)
        old_xp = self.character.xp
        old_level = self.character.level
        old_bonus = self.character.proficiency_bonus
        old_throws = Dice(self.character.hit_dice).throws
        old_max_hp = self.character.max_hp
        self.character.increase_xp(new_xp)
        assert self.character.xp == old_xp + new_xp
        assert self.character.level == old_level + 1
        assert self.character.proficiency_bonus == old_bonus + 2
        assert Dice(self.character.hit_dice).throws == old_throws + 1
        assert self.character.max_hp == old_max_hp + self.character.hp_increase

    def test_xp_increase_several_level_increase(self):
        new_xp = 50_000
        old_xp = self.character.xp
        old_throws = Dice(self.character.hit_dice).throws
        old_max_hp = self.character.max_hp
        self.character.increase_xp(new_xp)
        assert self.character.xp == old_xp + new_xp
        assert self.character.level == 9
        assert self.character.proficiency_bonus == 24
        assert Dice(self.character.hit_dice).throws == old_throws + 8
        assert self.character.max_hp == old_max_hp + self.character.hp_increase * 8
