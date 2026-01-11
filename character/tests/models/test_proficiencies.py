import pytest

from character.models.proficiencies import (
    ArmorProficiency,
    SavingThrowProficiency,
    SkillProficiency,
    ToolProficiency,
    WeaponProficiency,
)

from ..factories import (
    AbilityTypeFactory,
    ArmorSettingsFactory,
    CharacterFactory,
    ToolSettingsFactory,
    WeponSettingsFactory,
)


@pytest.fixture
def character():
    return CharacterFactory(name="proficiency_test_char")


@pytest.mark.django_db
class TestArmorProficiency:
    def test_creation(self, character):
        armor = ArmorSettingsFactory()
        proficiency = ArmorProficiency.objects.create(character=character, armor=armor)
        assert proficiency.character == character
        assert proficiency.armor == armor

    def test_str(self, character):
        armor = ArmorSettingsFactory()
        proficiency = ArmorProficiency.objects.create(character=character, armor=armor)
        assert str(proficiency) == str(armor)

    def test_cascade_delete_on_character(self, character):
        armor = ArmorSettingsFactory()
        ArmorProficiency.objects.create(character=character, armor=armor)
        character_id = character.id
        character.delete()
        assert not ArmorProficiency.objects.filter(character_id=character_id).exists()


@pytest.mark.django_db
class TestWeaponProficiency:
    def test_creation(self, character):
        weapon = WeponSettingsFactory()
        proficiency = WeaponProficiency.objects.create(
            character=character, weapon=weapon
        )
        assert proficiency.character == character
        assert proficiency.weapon == weapon

    def test_str(self, character):
        weapon = WeponSettingsFactory()
        proficiency = WeaponProficiency.objects.create(
            character=character, weapon=weapon
        )
        assert str(proficiency) == str(weapon)

    def test_cascade_delete_on_character(self, character):
        weapon = WeponSettingsFactory()
        WeaponProficiency.objects.create(character=character, weapon=weapon)
        character_id = character.id
        character.delete()
        assert not WeaponProficiency.objects.filter(character_id=character_id).exists()


@pytest.mark.django_db
class TestToolProficiency:
    def test_creation(self, character):
        tool = ToolSettingsFactory()
        proficiency = ToolProficiency.objects.create(character=character, tool=tool)
        assert proficiency.character == character
        assert proficiency.tool == tool

    def test_str(self, character):
        tool = ToolSettingsFactory()
        proficiency = ToolProficiency.objects.create(character=character, tool=tool)
        assert str(proficiency) == str(tool)

    def test_cascade_delete_on_character(self, character):
        tool = ToolSettingsFactory()
        ToolProficiency.objects.create(character=character, tool=tool)
        character_id = character.id
        character.delete()
        assert not ToolProficiency.objects.filter(character_id=character_id).exists()


@pytest.mark.django_db
class TestSavingThrowProficiency:
    def test_creation(self, character):
        ability_type = AbilityTypeFactory(name="STR")
        proficiency = SavingThrowProficiency.objects.create(
            character=character, ability_type=ability_type
        )
        assert proficiency.character == character
        assert proficiency.ability_type == ability_type

    def test_str(self, character):
        ability_type = AbilityTypeFactory(name="DEX")
        proficiency = SavingThrowProficiency.objects.create(
            character=character, ability_type=ability_type
        )
        assert str(proficiency) == str(ability_type)

    def test_cascade_delete_on_character(self, character):
        ability_type = AbilityTypeFactory(name="CON")
        SavingThrowProficiency.objects.create(
            character=character, ability_type=ability_type
        )
        character_id = character.id
        character.delete()
        assert not SavingThrowProficiency.objects.filter(
            character_id=character_id
        ).exists()


@pytest.mark.django_db
class TestSkillProficiency:
    @pytest.fixture
    def skill(self):
        from character.models.skills import Skill

        ability_type = AbilityTypeFactory(name="DEX")
        skill, _ = Skill.objects.get_or_create(
            name="Acrobatics", defaults={"ability_type": ability_type}
        )
        return skill

    def test_creation(self, character, skill):
        proficiency = SkillProficiency.objects.create(character=character, skill=skill)
        assert proficiency.character == character
        assert proficiency.skill == skill

    def test_str(self, character, skill):
        proficiency = SkillProficiency.objects.create(character=character, skill=skill)
        assert str(proficiency) == str(skill)

    def test_cascade_delete_on_character(self, character, skill):
        SkillProficiency.objects.create(character=character, skill=skill)
        character_id = character.id
        character.delete()
        assert not SkillProficiency.objects.filter(character_id=character_id).exists()
