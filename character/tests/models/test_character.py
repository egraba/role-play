import pytest
from faker import Faker

from character.constants.abilities import AbilityName
from character.constants.character import Gender
from character.constants.races import SenseName
from character.models.character import Character
from character.models.proficiencies import SavingThrowProficiency
from character.models.races import Sense
from game.constants.events import Against, RollType
from utils.dice import DiceString

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
        assert character.gender == Gender.MALE
        assert character.ac == 0

    def test_str(self, character):
        assert str(character) == character.name

    def test_strength(self, character):
        assert character.strength == character.abilities.get(
            ability_type__name=AbilityName.STRENGTH
        )

    def test_dexterity(self, character):
        assert character.dexterity == character.abilities.get(
            ability_type__name=AbilityName.DEXTERITY
        )

    def test_constitution(self, character):
        assert character.constitution == character.abilities.get(
            ability_type__name=AbilityName.CONSTITUTION
        )

    def test_intelligence(self, character):
        assert character.intelligence == character.abilities.get(
            ability_type__name=AbilityName.INTELLIGENCE
        )

    def test_wisdom(self, character):
        assert character.wisdom == character.abilities.get(
            ability_type__name=AbilityName.WISDOM
        )

    def test_charisma(self, character):
        assert character.charisma == character.abilities.get(
            ability_type__name=AbilityName.CHARISMA
        )

    @pytest.mark.parametrize(
        "level,expected_bonus",
        [
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (5, 3),
            (6, 3),
            (7, 3),
            (8, 3),
            (9, 4),
            (10, 4),
            (11, 4),
            (12, 4),
            (13, 5),
            (14, 5),
            (15, 5),
            (16, 5),
            (17, 6),
            (18, 6),
            (19, 6),
            (20, 6),
        ],
    )
    def test_proficiency_bonus(self, level, expected_bonus):
        character = CharacterFactory(level=level)
        assert character.proficiency_bonus == expected_bonus

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
        old_throws = DiceString(character.hit_dice).nb_throws
        old_max_hp = character.max_hp
        character.increase_xp(new_xp)
        assert character.xp == old_xp + new_xp
        assert character.level == old_level + 1
        assert DiceString(character.hit_dice).nb_throws == old_throws + 1
        assert character.max_hp == old_max_hp + character.hp_increase

    def test_xp_increase_several_level_increase(self, character):
        new_xp = 50_000
        old_xp = character.xp
        old_throws = DiceString(character.hit_dice).nb_throws
        old_max_hp = character.max_hp
        character.increase_xp(new_xp)
        assert character.xp == old_xp + new_xp
        assert character.level == 9
        assert DiceString(character.hit_dice).nb_throws == old_throws + 8
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

    def test_has_advantage_dwarven_resilience(self, character):
        character.senses.add(Sense.objects.get(name=SenseName.DWARVEN_RESILIENCE))
        assert character.has_advantage(RollType.SAVING_THROW, Against.POISON)

    def test_has_advantage_fey_ancestry(self, character):
        character.senses.add(Sense.objects.get(name=SenseName.FEY_ANCESTRY))
        assert character.has_advantage(RollType.SAVING_THROW, Against.CHARM)

    def test_has_advantage_brave(self, character):
        character.senses.add(Sense.objects.get(name=SenseName.BRAVE))
        assert character.has_advantage(RollType.SAVING_THROW, Against.BEING_FRIGHTENED)

    def test_has_advantage_not_valid(self, character):
        fake = Faker()
        assert not character.has_advantage(fake.enum(RollType), fake.enum(Against))

    def test_has_disadvantage(self, character):
        fake = Faker()
        assert not character.has_disadvantage(fake.enum(RollType), fake.enum(Against))
