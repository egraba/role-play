import pytest

from character.character_attributes_builders import BackgroundBuilder
from character.constants.backgrounds import BACKGROUNDS, Background
from character.constants.equipment import ToolName
from character.constants.feats import FeatName
from character.constants.skills import SkillName
from character.models.feats import CharacterFeat
from character.models.proficiencies import SkillProficiency, ToolProficiency

from .factories import CharacterFactory, FeatFactory


@pytest.mark.django_db
class TestBackgroundBuilder:
    @pytest.fixture
    def acolyte_character(self):
        return CharacterFactory(background=Background.ACOLYTE)

    @pytest.fixture
    def criminal_character(self):
        return CharacterFactory(background=Background.CRIMINAL)

    @pytest.fixture
    def sage_character(self):
        return CharacterFactory(background=Background.SAGE)

    @pytest.fixture
    def soldier_character(self):
        return CharacterFactory(background=Background.SOLDIER)

    def test_init(self, acolyte_character):
        builder = BackgroundBuilder(acolyte_character)
        assert builder.character == acolyte_character
        assert builder.background == Background.ACOLYTE


@pytest.mark.django_db
class TestBackgroundBuilderSkillProficiencies:
    def test_acolyte_skill_proficiencies(self):
        character = CharacterFactory(background=Background.ACOLYTE)
        builder = BackgroundBuilder(character)
        builder._add_skill_proficiencies()

        skills = set(
            sp.skill.name for sp in SkillProficiency.objects.filter(character=character)
        )
        assert skills == {SkillName.INSIGHT, SkillName.RELIGION}

    def test_criminal_skill_proficiencies(self):
        character = CharacterFactory(background=Background.CRIMINAL)
        builder = BackgroundBuilder(character)
        builder._add_skill_proficiencies()

        skills = set(
            sp.skill.name for sp in SkillProficiency.objects.filter(character=character)
        )
        assert skills == {SkillName.SLEIGHT_OF_HAND, SkillName.STEALTH}

    def test_sage_skill_proficiencies(self):
        character = CharacterFactory(background=Background.SAGE)
        builder = BackgroundBuilder(character)
        builder._add_skill_proficiencies()

        skills = set(
            sp.skill.name for sp in SkillProficiency.objects.filter(character=character)
        )
        assert skills == {SkillName.ARCANA, SkillName.HISTORY}

    def test_soldier_skill_proficiencies(self):
        character = CharacterFactory(background=Background.SOLDIER)
        builder = BackgroundBuilder(character)
        builder._add_skill_proficiencies()

        skills = set(
            sp.skill.name for sp in SkillProficiency.objects.filter(character=character)
        )
        assert skills == {SkillName.ATHLETICS, SkillName.INTIMIDATION}


@pytest.mark.django_db
class TestBackgroundBuilderToolProficiency:
    def test_acolyte_tool_proficiency(self):
        character = CharacterFactory(background=Background.ACOLYTE)
        builder = BackgroundBuilder(character)
        builder._add_tool_proficiency()

        tool_prof = ToolProficiency.objects.filter(character=character).first()
        assert tool_prof is not None
        assert tool_prof.tool.name == ToolName.CALLIGRAPHERS_SUPPLIES

    def test_criminal_tool_proficiency(self):
        character = CharacterFactory(background=Background.CRIMINAL)
        builder = BackgroundBuilder(character)
        builder._add_tool_proficiency()

        tool_prof = ToolProficiency.objects.filter(character=character).first()
        assert tool_prof is not None
        assert tool_prof.tool.name == ToolName.THIEVES_TOOLS

    def test_sage_tool_proficiency(self):
        character = CharacterFactory(background=Background.SAGE)
        builder = BackgroundBuilder(character)
        builder._add_tool_proficiency()

        tool_prof = ToolProficiency.objects.filter(character=character).first()
        assert tool_prof is not None
        assert tool_prof.tool.name == ToolName.CALLIGRAPHERS_SUPPLIES

    def test_soldier_no_automatic_tool_proficiency(self):
        """Soldier has gaming set choice, not automatic tool proficiency."""
        character = CharacterFactory(background=Background.SOLDIER)
        builder = BackgroundBuilder(character)
        builder._add_tool_proficiency()

        # Soldier has None for tool_proficiency (choice handled in form)
        tool_prof = ToolProficiency.objects.filter(character=character).first()
        assert tool_prof is None


@pytest.mark.django_db
class TestBackgroundBuilderOriginFeat:
    @pytest.fixture(autouse=True)
    def setup_feats(self):
        """Ensure feats exist in database."""
        FeatFactory(name=FeatName.ALERT)
        FeatFactory(name=FeatName.MAGIC_INITIATE_CLERIC)
        FeatFactory(name=FeatName.MAGIC_INITIATE_WIZARD)
        FeatFactory(name=FeatName.SAVAGE_ATTACKER)

    def test_acolyte_origin_feat(self):
        character = CharacterFactory(background=Background.ACOLYTE)
        builder = BackgroundBuilder(character)
        builder._add_origin_feat()

        assert character.feats.count() == 1
        assert character.feats.first().name == FeatName.MAGIC_INITIATE_CLERIC
        char_feat = CharacterFeat.objects.get(character=character)
        assert char_feat.granted_by == "background"

    def test_criminal_origin_feat(self):
        character = CharacterFactory(background=Background.CRIMINAL)
        builder = BackgroundBuilder(character)
        builder._add_origin_feat()

        assert character.feats.count() == 1
        assert character.feats.first().name == FeatName.ALERT

    def test_sage_origin_feat(self):
        character = CharacterFactory(background=Background.SAGE)
        builder = BackgroundBuilder(character)
        builder._add_origin_feat()

        assert character.feats.count() == 1
        assert character.feats.first().name == FeatName.MAGIC_INITIATE_WIZARD

    def test_soldier_origin_feat(self):
        character = CharacterFactory(background=Background.SOLDIER)
        builder = BackgroundBuilder(character)
        builder._add_origin_feat()

        assert character.feats.count() == 1
        assert character.feats.first().name == FeatName.SAVAGE_ATTACKER


@pytest.mark.django_db
class TestBackgroundBuilderStartingGold:
    def test_adds_50_gp(self):
        character = CharacterFactory(background=Background.ACOLYTE)
        initial_gp = character.inventory.gp
        builder = BackgroundBuilder(character)
        builder._add_starting_gold()

        character.inventory.refresh_from_db()
        assert character.inventory.gp == initial_gp + 50

    def test_stacks_with_existing_gold(self):
        character = CharacterFactory(background=Background.CRIMINAL)
        character.inventory.gp = 100
        character.inventory.save()

        builder = BackgroundBuilder(character)
        builder._add_starting_gold()

        character.inventory.refresh_from_db()
        assert character.inventory.gp == 150


@pytest.mark.django_db
class TestBackgroundBuilderPersonalitySelection:
    def test_select_personality_trait(self):
        character = CharacterFactory(background=Background.ACOLYTE)
        builder = BackgroundBuilder(character)
        builder._select_personality_trait()

        assert (
            character.personality_trait
            in BACKGROUNDS[Background.ACOLYTE]["personality_traits"].values()
        )

    def test_select_ideal(self):
        character = CharacterFactory(background=Background.CRIMINAL)
        builder = BackgroundBuilder(character)
        builder._select_ideal()

        assert character.ideal in BACKGROUNDS[Background.CRIMINAL]["ideals"].values()

    def test_select_bond(self):
        character = CharacterFactory(background=Background.SAGE)
        builder = BackgroundBuilder(character)
        builder._select_bond()

        assert character.bond in BACKGROUNDS[Background.SAGE]["bonds"].values()

    def test_select_flaw(self):
        character = CharacterFactory(background=Background.SOLDIER)
        builder = BackgroundBuilder(character)
        builder._select_flaw()

        assert character.flaw in BACKGROUNDS[Background.SOLDIER]["flaws"].values()


@pytest.mark.django_db
class TestBackgroundBuilderBuild:
    @pytest.fixture(autouse=True)
    def setup_feats(self):
        """Ensure feats exist in database."""
        FeatFactory(name=FeatName.ALERT)
        FeatFactory(name=FeatName.MAGIC_INITIATE_CLERIC)
        FeatFactory(name=FeatName.MAGIC_INITIATE_WIZARD)
        FeatFactory(name=FeatName.SAVAGE_ATTACKER)

    def test_build_acolyte(self):
        """Test full build for Acolyte background."""
        character = CharacterFactory(background=Background.ACOLYTE)
        initial_gp = character.inventory.gp

        builder = BackgroundBuilder(character)
        builder.build()

        # Check skill proficiencies
        skills = set(
            sp.skill.name for sp in SkillProficiency.objects.filter(character=character)
        )
        assert skills == {SkillName.INSIGHT, SkillName.RELIGION}

        # Check tool proficiency
        tool_prof = ToolProficiency.objects.filter(character=character).first()
        assert tool_prof.tool.name == ToolName.CALLIGRAPHERS_SUPPLIES

        # Check origin feat
        assert character.feats.first().name == FeatName.MAGIC_INITIATE_CLERIC

        # Check starting gold
        character.inventory.refresh_from_db()
        assert character.inventory.gp == initial_gp + 50

        # Check personality selections
        assert (
            character.personality_trait
            in BACKGROUNDS[Background.ACOLYTE]["personality_traits"].values()
        )
        assert character.ideal in BACKGROUNDS[Background.ACOLYTE]["ideals"].values()
        assert character.bond in BACKGROUNDS[Background.ACOLYTE]["bonds"].values()
        assert character.flaw in BACKGROUNDS[Background.ACOLYTE]["flaws"].values()

    def test_build_all_backgrounds(self):
        """Test build works for all backgrounds."""
        for background in Background:
            character = CharacterFactory(background=background)
            builder = BackgroundBuilder(character)
            builder.build()

            # Verify skill proficiencies were added
            skill_count = SkillProficiency.objects.filter(character=character).count()
            assert skill_count == 2, f"{background} should have 2 skill proficiencies"

            # Verify origin feat was added
            assert character.feats.count() == 1, f"{background} should have 1 feat"

            # Verify personality traits were set
            assert character.personality_trait, f"{background} should have personality"
            assert character.ideal, f"{background} should have ideal"
            assert character.bond, f"{background} should have bond"
            assert character.flaw, f"{background} should have flaw"
