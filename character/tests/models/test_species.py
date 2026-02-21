import pytest

from character.constants.species import SpeciesName, SpeciesTraitName
from character.models.species import Species, SpeciesTrait

from ..factories import CharacterFactory, SpeciesFactory


@pytest.mark.django_db
class TestSpeciesTraitModel:
    def test_creation(self):
        # Use get_or_create since fixtures may already have loaded these
        trait, _ = SpeciesTrait.objects.get_or_create(
            name=SpeciesTraitName.DWARVEN_RESILIENCE,
            defaults={"description": "Resistance to poison"},
        )
        assert trait.name == SpeciesTraitName.DWARVEN_RESILIENCE

    def test_str(self):
        trait, _ = SpeciesTrait.objects.get_or_create(
            name=SpeciesTraitName.BRAVE,
            defaults={
                "description": "Advantage on saving throws against being frightened"
            },
        )
        assert str(trait) == "Brave"

    def test_all_traits_valid(self):
        """Verify all SpeciesTraitName choices are valid."""
        for name, _ in SpeciesTraitName.choices:
            trait, _ = SpeciesTrait.objects.get_or_create(
                name=name,
                defaults={"description": f"Test trait for {name}"},
            )
            assert trait.name == name


@pytest.mark.django_db
class TestSpeciesModel:
    def test_creation(self):
        species = SpeciesFactory(
            name=SpeciesName.DWARF,
            size="M",
            speed=30,
            darkvision=120,
        )
        assert species.name == SpeciesName.DWARF
        assert species.size == "M"
        assert species.speed == 30
        assert species.darkvision == 120

    def test_str(self):
        species = SpeciesFactory(name=SpeciesName.ELF)
        assert str(species) == "Elf"

    def test_all_species_valid(self):
        """Verify all SpeciesName choices are valid."""
        for name, _ in SpeciesName.choices:
            species = SpeciesFactory(name=name)
            assert species.name == name

    def test_traits_relationship(self):
        species = SpeciesFactory(name=SpeciesName.HALFLING)
        # Clear any existing traits from fixture
        species.traits.clear()
        trait1, _ = SpeciesTrait.objects.get_or_create(
            name=SpeciesTraitName.BRAVE,
            defaults={
                "description": "Advantage on saving throws against being frightened"
            },
        )
        trait2, _ = SpeciesTrait.objects.get_or_create(
            name=SpeciesTraitName.LUCKY,
            defaults={"description": "Reroll 1s on d20 rolls"},
        )
        species.traits.add(trait1, trait2)
        assert species.traits.count() == 2
        assert trait1 in species.traits.all()
        assert trait2 in species.traits.all()

    def test_languages_relationship(self):
        from character.models.races import Language

        species = SpeciesFactory(name=SpeciesName.DWARF)
        common = Language.objects.get_or_create(name="common", language_type="S")[0]
        dwarvish = Language.objects.get_or_create(name="dwarvish", language_type="S")[0]
        species.languages.add(common, dwarvish)
        assert species.languages.count() >= 2

    def test_no_darkvision(self):
        species = SpeciesFactory(name=SpeciesName.HUMAN, darkvision=0)
        assert species.darkvision == 0

    def test_small_size(self):
        species = SpeciesFactory(name=SpeciesName.HALFLING, size="S")
        assert species.size == "S"


@pytest.mark.django_db
class TestCharacterSpeciesRelation:
    def test_character_has_species(self):
        species = SpeciesFactory(name=SpeciesName.ELF)
        character = CharacterFactory(species=species)
        assert character.species == species
        assert character.species.name == SpeciesName.ELF

    def test_character_species_traits(self):
        trait, _ = SpeciesTrait.objects.get_or_create(
            name=SpeciesTraitName.FEY_ANCESTRY,
            defaults={"description": "Advantage vs charmed"},
        )
        species = SpeciesFactory(name=SpeciesName.ELF)
        # Clear existing traits and add only our test trait
        species.traits.clear()
        species.traits.add(trait)
        character = CharacterFactory(species=species)
        assert character.species.traits.count() == 1
        assert trait in character.species.traits.all()

    def test_character_has_trait_method(self):
        trait, _ = SpeciesTrait.objects.get_or_create(
            name=SpeciesTraitName.DWARVEN_RESILIENCE,
            defaults={"description": "Poison resistance"},
        )
        species = SpeciesFactory(name=SpeciesName.DWARF)
        species.traits.add(trait)
        character = CharacterFactory(species=species)
        assert character._has_trait(SpeciesTraitName.DWARVEN_RESILIENCE.value)
        assert not character._has_trait(SpeciesTraitName.FEY_ANCESTRY.value)

    def test_character_without_species(self):
        character = CharacterFactory(species=None)
        assert character.species is None
        assert not character._has_trait(SpeciesTraitName.BRAVE.value)


@pytest.mark.django_db
class TestNewSRDSpecies:
    """Verify all 5 new SRD 5.2.1 species load from fixtures correctly."""

    def test_all_nine_species_exist(self):
        assert Species.objects.count() == 9

    def test_dragonborn_loaded(self):
        species = Species.objects.get(name=SpeciesName.DRAGONBORN)
        assert species.size == "M"
        assert species.speed == 30
        assert species.darkvision == 60  # SRD 5.2.1 Dragonborn has darkvision
        assert (
            species.traits.count() == 4
        )  # draconic_ancestry, breath_weapon, draconic_damage_resistance, draconic_flight

    def test_gnome_loaded(self):
        species = Species.objects.get(name=SpeciesName.GNOME)
        assert species.size == "S"
        assert species.darkvision == 60
        assert species.traits.count() == 2  # gnomish_cunning, gnomish_lineage

    def test_goliath_loaded(self):
        species = Species.objects.get(name=SpeciesName.GOLIATH)
        assert species.speed == 35  # Giant Ancestry +5 ft
        assert species.darkvision == 0
        assert species.traits.count() == 3  # giant_ancestry, large_form, powerful_build

    def test_orc_loaded(self):
        species = Species.objects.get(name=SpeciesName.ORC)
        assert species.darkvision == 120  # SRD 5.2.1 Orc has 120 ft darkvision
        assert species.traits.count() == 2  # adrenaline_rush, relentless_endurance

    def test_tiefling_loaded(self):
        species = Species.objects.get(name=SpeciesName.TIEFLING)
        assert species.darkvision == 60
        assert species.traits.count() == 2  # fiendish_legacy, otherworldly_presence

    def test_all_species_name_choices_have_fixture(self):
        for name, _ in SpeciesName.choices:
            assert Species.objects.filter(name=name).exists(), (
                f"Missing fixture for species: {name}"
            )
