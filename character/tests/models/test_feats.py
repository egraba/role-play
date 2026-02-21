import pytest

from character.constants.feats import FeatName, FeatType
from character.models.feats import CharacterFeat, Feat

from ..factories import CharacterFactory, CharacterFeatFactory, FeatFactory


@pytest.mark.django_db
class TestFeatModel:
    def test_creation(self):
        feat = FeatFactory(
            name=FeatName.ALERT,
            feat_type=FeatType.ORIGIN,
            description="Initiative bonus feat.",
        )
        assert feat.name == FeatName.ALERT
        assert feat.feat_type == FeatType.ORIGIN
        assert "initiative" in feat.description.lower()

    def test_str(self):
        feat = FeatFactory(name=FeatName.ALERT)
        assert str(feat) == "Alert"

    def test_str_magic_initiate_cleric(self):
        feat = FeatFactory(name=FeatName.MAGIC_INITIATE_CLERIC)
        assert str(feat) == "Magic Initiate (Cleric)"

    def test_str_magic_initiate_wizard(self):
        feat = FeatFactory(name=FeatName.MAGIC_INITIATE_WIZARD)
        assert str(feat) == "Magic Initiate (Wizard)"

    def test_str_savage_attacker(self):
        feat = FeatFactory(name=FeatName.SAVAGE_ATTACKER)
        assert str(feat) == "Savage Attacker"

    def test_all_feats_valid(self):
        """Verify all FeatName choices are valid."""
        for name, _ in FeatName.choices:
            feat = FeatFactory(name=name)
            assert feat.name == name

    def test_feat_type_origin(self):
        """Verify Origin feat type works."""
        feat = FeatFactory(name=FeatName.ALERT, feat_type=FeatType.ORIGIN)
        assert feat.feat_type == FeatType.ORIGIN

    def test_feat_type_general(self):
        """Verify General feat type works."""
        feat, _ = Feat.objects.update_or_create(
            name=FeatName.SAVAGE_ATTACKER,
            defaults={
                "feat_type": FeatType.GENERAL,
                "description": "Test general feat",
            },
        )
        assert feat.feat_type == FeatType.GENERAL

    def test_prerequisite_optional(self):
        """Feat prerequisite is optional."""
        feat = FeatFactory(name=FeatName.ALERT)
        assert feat.prerequisite == ""

    def test_prerequisite_can_be_set(self):
        """Feat prerequisite can be set."""
        feat, _ = Feat.objects.update_or_create(
            name=FeatName.MAGIC_INITIATE_CLERIC,
            defaults={
                "feat_type": FeatType.GENERAL,
                "description": "Test",
                "prerequisite": "Level 4",
            },
        )
        assert feat.prerequisite == "Level 4"

    def test_ordering(self):
        """Feats are ordered by name."""
        names = [
            FeatName.SAVAGE_ATTACKER,
            FeatName.ALERT,
            FeatName.MAGIC_INITIATE_CLERIC,
        ]
        for name in names:
            FeatFactory(name=name)
        feats = list(Feat.objects.filter(name__in=names))
        assert feats[0].name == FeatName.ALERT
        assert feats[1].name == FeatName.MAGIC_INITIATE_CLERIC
        assert feats[2].name == FeatName.SAVAGE_ATTACKER


@pytest.mark.django_db
class TestCharacterFeatModel:
    @pytest.fixture
    def character(self):
        return CharacterFactory()

    @pytest.fixture
    def feat(self):
        return FeatFactory(name=FeatName.ALERT)

    def test_creation(self, character, feat):
        char_feat = CharacterFeat.objects.create(
            character=character, feat=feat, granted_by="background"
        )
        assert char_feat.character == character
        assert char_feat.feat == feat
        assert char_feat.granted_by == "background"

    def test_str(self, character, feat):
        char_feat = CharacterFeat.objects.create(
            character=character, feat=feat, granted_by="background"
        )
        assert str(char_feat) == f"{character.name}: {feat.name}"

    def test_granted_by_options(self, character, feat):
        """Test various granted_by sources."""
        for source in ["background", "species", "class", ""]:
            char_feat = CharacterFeat.objects.create(
                character=character, feat=feat, granted_by=source
            )
            assert char_feat.granted_by == source
            char_feat.delete()

    def test_unique_together_constraint(self, character, feat):
        """A character can only have one instance of each feat."""
        CharacterFeat.objects.create(character=character, feat=feat)
        with pytest.raises(Exception):  # IntegrityError
            CharacterFeat.objects.create(character=character, feat=feat)

    def test_character_feats_relation(self, character, feat):
        """Test the ManyToMany relationship works."""
        CharacterFeat.objects.create(
            character=character, feat=feat, granted_by="background"
        )
        assert character.feats.count() == 1
        assert character.feats.first() == feat

    def test_character_feats_related_name(self, character, feat):
        """Test the character_feats related_name works."""
        char_feat = CharacterFeat.objects.create(
            character=character, feat=feat, granted_by="background"
        )
        assert character.character_feats.count() == 1
        assert character.character_feats.first() == char_feat

    def test_multiple_feats_on_character(self, character):
        """A character can have multiple different feats."""
        alert = FeatFactory(name=FeatName.ALERT)
        savage = FeatFactory(name=FeatName.SAVAGE_ATTACKER)
        magic = FeatFactory(name=FeatName.MAGIC_INITIATE_CLERIC)

        CharacterFeat.objects.create(
            character=character, feat=alert, granted_by="background"
        )
        CharacterFeat.objects.create(
            character=character, feat=savage, granted_by="class"
        )
        CharacterFeat.objects.create(
            character=character, feat=magic, granted_by="species"
        )

        assert character.feats.count() == 3

    def test_cascade_delete_on_character(self, character, feat):
        """CharacterFeat should be deleted when character is deleted."""
        CharacterFeat.objects.create(character=character, feat=feat)
        character_id = character.id
        character.delete()
        assert not CharacterFeat.objects.filter(character_id=character_id).exists()

    def test_cascade_delete_on_feat(self, character, feat):
        """CharacterFeat should be deleted when feat is deleted."""
        CharacterFeat.objects.create(character=character, feat=feat)
        feat_name = feat.name
        feat.delete()
        assert not CharacterFeat.objects.filter(feat_id=feat_name).exists()

    def test_factory(self):
        """Test CharacterFeatFactory works correctly."""
        char_feat = CharacterFeatFactory()
        assert char_feat.character is not None
        assert char_feat.feat is not None
        assert char_feat.granted_by == "background"


@pytest.mark.django_db
class TestSRDFeatCompleteness:
    """Verify all SRD 5.2.1 feats load from fixtures correctly."""

    def test_all_feat_names_have_fixture(self):
        for name, _ in FeatName.choices:
            assert Feat.objects.filter(name=name).exists(), (
                f"Missing fixture for feat: {name}"
            )

    def test_general_feat_count(self):
        general_count = Feat.objects.filter(feat_type=FeatType.GENERAL).count()
        assert general_count == 30, f"Expected 30 general feats, found {general_count}"

    def test_all_general_feats_have_description(self):
        feats = Feat.objects.filter(feat_type=FeatType.GENERAL)
        for feat in feats:
            assert feat.description, f"Feat {feat.name} has empty description"
