import pytest

from character.constants.klasses import ClassName
from character.models.klasses import CharacterClass, Class, ClassFeature

from ..factories import (
    AbilityTypeFactory,
    CharacterClassFactory,
    CharacterFactory,
    ClassFactory,
    ClassFeatureFactory,
)


@pytest.mark.django_db
class TestClassModel:
    def test_creation(self):
        ability_type = AbilityTypeFactory(name="STR")
        klass = ClassFactory(
            name=ClassName.FIGHTER,
            description="A martial warrior.",
            hit_die=10,
            hp_first_level=10,
            hp_higher_levels=6,
            primary_ability=ability_type,
            armor_proficiencies=["LA", "MA", "HA", "SH"],
            weapon_proficiencies=["simple", "martial"],
            starting_wealth_dice="5d4",
        )
        assert klass.name == ClassName.FIGHTER
        assert klass.hit_die == 10
        assert klass.hp_first_level == 10
        assert klass.hp_higher_levels == 6
        assert klass.primary_ability == ability_type
        assert "LA" in klass.armor_proficiencies
        assert "martial" in klass.weapon_proficiencies
        assert klass.starting_wealth_dice == "5d4"

    def test_str(self):
        klass = ClassFactory(name=ClassName.FIGHTER)
        assert str(klass) == "Fighter"

    def test_str_cleric(self):
        klass = ClassFactory(name=ClassName.CLERIC)
        assert str(klass) == "Cleric"

    def test_str_rogue(self):
        klass = ClassFactory(name=ClassName.ROGUE)
        assert str(klass) == "Rogue"

    def test_str_wizard(self):
        klass = ClassFactory(name=ClassName.WIZARD)
        assert str(klass) == "Wizard"

    def test_all_classes_valid(self):
        """Verify all ClassName choices are valid."""
        for name, _ in ClassName.choices:
            klass = ClassFactory(name=name)
            assert klass.name == name

    def test_saving_throws_relationship(self):
        """Test M2M saving_throws relationship."""
        str_type = AbilityTypeFactory(name="STR")
        con_type = AbilityTypeFactory(name="CON")
        klass = ClassFactory(name=ClassName.FIGHTER)
        klass.saving_throws.add(str_type, con_type)

        assert klass.saving_throws.count() == 2
        assert str_type in klass.saving_throws.all()
        assert con_type in klass.saving_throws.all()

    def test_features_relationship(self):
        """Test reverse relationship to ClassFeature."""
        klass = ClassFactory(name=ClassName.FIGHTER)
        feature1 = ClassFeatureFactory(klass=klass, name="Fighting Style", level=1)
        feature2 = ClassFeatureFactory(klass=klass, name="Second Wind", level=1)

        assert klass.features.count() == 2
        assert feature1 in klass.features.all()
        assert feature2 in klass.features.all()

    def test_ordering(self):
        """Classes are ordered by name."""
        ClassFactory(name=ClassName.WIZARD)
        ClassFactory(name=ClassName.CLERIC)
        ClassFactory(name=ClassName.FIGHTER)
        classes = list(Class.objects.all())
        assert classes[0].name == ClassName.CLERIC
        assert classes[1].name == ClassName.FIGHTER


@pytest.mark.django_db
class TestClassFeatureModel:
    @pytest.fixture
    def fighter(self):
        return ClassFactory(name=ClassName.FIGHTER)

    def test_creation(self, fighter):
        feature = ClassFeature.objects.create(
            name="Fighting Style",
            klass=fighter,
            level=1,
            description="Choose a Fighting Style feat.",
        )
        assert feature.name == "Fighting Style"
        assert feature.klass == fighter
        assert feature.level == 1
        assert "Fighting Style" in feature.description

    def test_str(self, fighter):
        feature = ClassFeature.objects.create(
            name="Second Wind",
            klass=fighter,
            level=1,
            description="Heal yourself.",
        )
        assert str(feature) == "Second Wind (Level 1)"

    def test_str_higher_level(self, fighter):
        feature = ClassFeature.objects.create(
            name="Action Surge",
            klass=fighter,
            level=2,
            description="Take an additional action.",
        )
        assert str(feature) == "Action Surge (Level 2)"

    def test_unique_together_constraint(self, fighter):
        """A class can only have one feature with the same name."""
        ClassFeature.objects.create(
            name="Fighting Style", klass=fighter, level=1, description="Test"
        )
        with pytest.raises(Exception):
            ClassFeature.objects.create(
                name="Fighting Style", klass=fighter, level=4, description="Another"
            )

    def test_ordering(self, fighter):
        """Features are ordered by class, level, name."""
        ClassFeature.objects.create(
            name="Action Surge", klass=fighter, level=2, description="Test"
        )
        ClassFeature.objects.create(
            name="Fighting Style", klass=fighter, level=1, description="Test"
        )
        ClassFeature.objects.create(
            name="Second Wind", klass=fighter, level=1, description="Test"
        )

        features = list(ClassFeature.objects.all())
        assert features[0].level == 1
        assert features[0].name == "Fighting Style"
        assert features[1].level == 1
        assert features[1].name == "Second Wind"
        assert features[2].level == 2

    def test_cascade_delete_on_class(self, fighter):
        """ClassFeature should be deleted when class is deleted."""
        ClassFeature.objects.create(
            name="Fighting Style", klass=fighter, level=1, description="Test"
        )
        class_name = fighter.name
        fighter.delete()
        assert not ClassFeature.objects.filter(klass_id=class_name).exists()

    def test_factory(self):
        """Test ClassFeatureFactory works correctly."""
        feature = ClassFeatureFactory()
        assert feature.klass is not None
        assert feature.level >= 1
        assert feature.description != ""


@pytest.mark.django_db
class TestCharacterClassModel:
    @pytest.fixture
    def character(self):
        return CharacterFactory(name="test_character")

    @pytest.fixture
    def fighter(self):
        return ClassFactory(name=ClassName.FIGHTER)

    def test_creation(self, character, fighter):
        char_class = CharacterClass.objects.create(
            character=character, klass=fighter, level=1, is_primary=True
        )
        assert char_class.character == character
        assert char_class.klass == fighter
        assert char_class.level == 1
        assert char_class.is_primary is True

    def test_str(self, character, fighter):
        char_class = CharacterClass.objects.create(
            character=character, klass=fighter, level=5, is_primary=True
        )
        assert str(char_class) == f"{character.name}: {fighter.name} 5"

    def test_unique_together_constraint(self, character, fighter):
        """A character can only have one instance of each class."""
        CharacterClass.objects.create(character=character, klass=fighter)
        with pytest.raises(Exception):
            CharacterClass.objects.create(character=character, klass=fighter)

    def test_character_classes_relation(self, character, fighter):
        """Test the ManyToMany relationship works."""
        CharacterClass.objects.create(
            character=character, klass=fighter, level=1, is_primary=True
        )
        assert character.classes.count() == 1
        assert character.classes.first() == fighter

    def test_character_classes_related_name(self, character, fighter):
        """Test the character_classes related_name works."""
        char_class = CharacterClass.objects.create(
            character=character, klass=fighter, level=1, is_primary=True
        )
        assert character.character_classes.count() == 1
        assert character.character_classes.first() == char_class

    def test_primary_class_property(self, character, fighter):
        """Test Character.primary_class property."""
        CharacterClass.objects.create(
            character=character, klass=fighter, level=3, is_primary=True
        )
        assert character.primary_class == fighter

    def test_primary_class_none_when_no_classes(self, character):
        """Test primary_class returns None when character has no classes."""
        assert character.primary_class is None

    def test_class_level_property(self, character, fighter):
        """Test Character.class_level property."""
        CharacterClass.objects.create(
            character=character, klass=fighter, level=7, is_primary=True
        )
        assert character.class_level == 7

    def test_class_level_zero_when_no_classes(self, character):
        """Test class_level returns 0 when character has no classes."""
        assert character.class_level == 0

    def test_multiclass_support(self, character):
        """A character can have multiple different classes."""
        fighter = ClassFactory(name=ClassName.FIGHTER)
        rogue = ClassFactory(name=ClassName.ROGUE)

        CharacterClass.objects.create(
            character=character, klass=fighter, level=5, is_primary=True
        )
        CharacterClass.objects.create(
            character=character, klass=rogue, level=3, is_primary=False
        )

        assert character.classes.count() == 2
        assert character.primary_class == fighter

    def test_cascade_delete_on_character(self, character, fighter):
        """CharacterClass should be deleted when character is deleted."""
        CharacterClass.objects.create(character=character, klass=fighter)
        character_id = character.id
        character.delete()
        assert not CharacterClass.objects.filter(character_id=character_id).exists()

    def test_protect_on_class_delete(self, character, fighter):
        """Class should be protected from deletion if characters have it."""
        CharacterClass.objects.create(character=character, klass=fighter)
        with pytest.raises(Exception):
            fighter.delete()

    def test_factory(self):
        """Test CharacterClassFactory works correctly."""
        char_class = CharacterClassFactory()
        assert char_class.character is not None
        assert char_class.klass is not None
        assert char_class.level == 1
        assert char_class.is_primary is True
