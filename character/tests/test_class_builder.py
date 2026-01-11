import pytest

from character.character_attributes_builders import ClassBuilder
from character.constants.classes import ClassName
from character.models.classes import CharacterClass
from character.models.proficiencies import SavingThrowProficiency

from .factories import AbilityTypeFactory, CharacterFactory, ClassFactory


@pytest.fixture
def fighter_class():
    """Create a Fighter class with saving throws configured."""
    str_type = AbilityTypeFactory(name="STR")
    con_type = AbilityTypeFactory(name="CON")
    klass = ClassFactory(
        name=ClassName.FIGHTER,
        hit_die=10,
        hp_first_level=10,
        hp_higher_levels=6,
        primary_ability=str_type,
        armor_proficiencies=["LA", "MA", "HA", "SH"],
        weapon_proficiencies=["simple", "martial"],
        starting_wealth_dice="5d4",
    )
    klass.saving_throws.add(str_type, con_type)
    return klass


@pytest.fixture
def character():
    """Create a character with abilities and inventory."""
    return CharacterFactory(name="test_class_builder_char")


@pytest.mark.django_db
class TestClassBuilder:
    def test_init(self, character, fighter_class):
        """Test ClassBuilder initialization."""
        builder = ClassBuilder(character, fighter_class)
        assert builder.character == character
        assert builder.klass == fighter_class

    def test_create_character_class(self, character, fighter_class):
        """Test creating CharacterClass junction record."""
        builder = ClassBuilder(character, fighter_class)
        builder._create_character_class()

        char_class = CharacterClass.objects.get(character=character)
        assert char_class.klass == fighter_class
        assert char_class.level == 1
        assert char_class.is_primary is True

    def test_apply_hit_points(self, character, fighter_class):
        """Test applying hit points from class."""
        builder = ClassBuilder(character, fighter_class)

        builder._apply_hit_points()

        # hit_dice should be "1d{hit_die}"
        assert character.hit_dice == "1d10"
        # HP = 100 + hp_first_level + constitution modifier
        con_mod = character.constitution.modifier
        expected_hp = 100 + 10 + con_mod
        assert character.hp == expected_hp
        assert character.max_hp == expected_hp
        assert character.hp_increase == 6

    def test_apply_saving_throw_proficiencies(self, character, fighter_class):
        """Test granting saving throw proficiencies from class."""
        builder = ClassBuilder(character, fighter_class)
        builder._apply_saving_throw_proficiencies()

        proficiencies = SavingThrowProficiency.objects.filter(character=character)
        assert proficiencies.count() == 2

        ability_names = {p.ability_type.name for p in proficiencies}
        assert "STR" in ability_names
        assert "CON" in ability_names

    def test_apply_armor_proficiencies(self, character, fighter_class):
        """Test armor proficiencies method exists (stub)."""
        builder = ClassBuilder(character, fighter_class)
        # Should not raise - currently a stub
        builder._apply_armor_proficiencies()

    def test_apply_weapon_proficiencies(self, character, fighter_class):
        """Test weapon proficiencies method exists (stub)."""
        builder = ClassBuilder(character, fighter_class)
        # Should not raise - currently a stub
        builder._apply_weapon_proficiencies()

    def test_add_starting_wealth(self, character, fighter_class):
        """Test adding starting wealth from class."""
        builder = ClassBuilder(character, fighter_class)
        original_gp = character.inventory.gp

        builder._add_starting_wealth()

        # 5d4 * 10 = 50-200 GP added
        added_gp = character.inventory.gp - original_gp
        assert 50 <= added_gp <= 200

    def test_build_full(self, character, fighter_class):
        """Test full build process."""
        builder = ClassBuilder(character, fighter_class)
        original_gp = character.inventory.gp

        builder.build()

        # Check CharacterClass was created
        assert CharacterClass.objects.filter(character=character).exists()
        char_class = CharacterClass.objects.get(character=character)
        assert char_class.klass == fighter_class
        assert char_class.is_primary is True

        # Check hit points were applied
        assert character.hit_dice == "1d10"
        con_mod = character.constitution.modifier
        expected_hp = 100 + 10 + con_mod
        assert character.hp == expected_hp
        assert character.max_hp == expected_hp
        assert character.hp_increase == 6

        # Check saving throw proficiencies
        proficiencies = SavingThrowProficiency.objects.filter(character=character)
        assert proficiencies.count() == 2

        # Check wealth was added
        added_gp = character.inventory.gp - original_gp
        assert 50 <= added_gp <= 200

    def test_build_with_wizard_class(self, character):
        """Test build with Wizard class (different stats)."""
        int_type = AbilityTypeFactory(name="INT")
        wis_type = AbilityTypeFactory(name="WIS")
        wizard = ClassFactory(
            name=ClassName.WIZARD,
            hit_die=6,
            hp_first_level=6,
            hp_higher_levels=4,
            primary_ability=int_type,
            armor_proficiencies=[],
            weapon_proficiencies=["simple"],
            starting_wealth_dice="4d4",
        )
        wizard.saving_throws.add(int_type, wis_type)

        builder = ClassBuilder(character, wizard)
        builder.build()

        # Check Wizard-specific values
        assert character.hit_dice == "1d6"
        con_mod = character.constitution.modifier
        expected_hp = 100 + 6 + con_mod
        assert character.hp == expected_hp
        assert character.hp_increase == 4

        # Check saving throws are INT and WIS
        proficiencies = SavingThrowProficiency.objects.filter(character=character)
        ability_names = {p.ability_type.name for p in proficiencies}
        assert "INT" in ability_names
        assert "WIS" in ability_names

    def test_build_with_rogue_class(self, character):
        """Test build with Rogue class."""
        dex_type = AbilityTypeFactory(name="DEX")
        int_type = AbilityTypeFactory(name="INT")
        rogue = ClassFactory(
            name=ClassName.ROGUE,
            hit_die=8,
            hp_first_level=8,
            hp_higher_levels=5,
            primary_ability=dex_type,
            armor_proficiencies=["LA"],
            weapon_proficiencies=["simple"],
            starting_wealth_dice="4d4",
        )
        rogue.saving_throws.add(dex_type, int_type)

        builder = ClassBuilder(character, rogue)
        builder.build()

        assert character.hit_dice == "1d8"
        assert character.hp_increase == 5

        proficiencies = SavingThrowProficiency.objects.filter(character=character)
        ability_names = {p.ability_type.name for p in proficiencies}
        assert "DEX" in ability_names
        assert "INT" in ability_names

    def test_character_primary_class_after_build(self, character, fighter_class):
        """Test Character.primary_class property works after build."""
        builder = ClassBuilder(character, fighter_class)
        builder.build()

        assert character.primary_class == fighter_class

    def test_character_class_level_after_build(self, character, fighter_class):
        """Test Character.class_level property works after build."""
        builder = ClassBuilder(character, fighter_class)
        builder.build()

        assert character.class_level == 1

    def test_character_classes_relation_after_build(self, character, fighter_class):
        """Test Character.classes M2M relation after build."""
        builder = ClassBuilder(character, fighter_class)
        builder.build()

        assert character.classes.count() == 1
        assert fighter_class in character.classes.all()
