import pytest
from django.db.models import Q
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from character.constants.abilities import AbilityName, AbilityScore
from character.constants.backgrounds import BACKGROUNDS, Background
from character.constants.equipment import ArmorName, GearName, ToolName, WeaponName
from character.constants.character import Gender
from character.constants.species import SpeciesName
from character.constants.skills import SkillName
from character.forms.backgrounds import (
    _get_gaming_set_tools,
    _get_holy_symbols,
)
from character.forms.equipment_choices_providers import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)
from character.forms.skills import _get_skills
from character.models.character import Character
from character.constants.classes import ClassName
from character.models.proficiencies import SavingThrowProficiency, SkillProficiency
from character.models.skills import Skill
from character.views.character import (
    CharacterCreateView,
    CharacterDetailView,
)
from game.tests.factories import GameFactory, PlayerFactory
from user.tests.factories import UserFactory

from ..factories import CharacterFactory, SpeciesFactory


@pytest.mark.django_db
class TestCharacterDetailView:
    def test_view_mapping(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterDetailView

    def test_template_mapping(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assertTemplateUsed(response, "character/character.html")

    def test_content_character_is_in_game(self, client, character):
        game = GameFactory()
        PlayerFactory(game=game, character=character)
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assertContains(response, game.name)


@pytest.fixture(scope="class")
def create_characters(django_db_blocker):
    with django_db_blocker.unblock():
        number_of_characters = 22
        for _ in range(number_of_characters):
            CharacterFactory()


@pytest.mark.django_db
class TestCharacterCreateView:
    path_name = "character-create"

    @pytest.fixture(autouse=True)
    def user_with_no_character(self, client):
        user = UserFactory(username="user-with-no-character")
        client.force_login(user)

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class, CharacterCreateView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertTemplateUsed(response, "character/character_create.html")

    @pytest.fixture
    def character_form(self):
        fake = Faker()
        # Create species in database for form to reference
        species = SpeciesFactory(name=fake.enum(enum_cls=SpeciesName))
        # Only use classes that have equipment/skills choices implemented
        supported_classes = [
            ClassName.CLERIC,
            ClassName.FIGHTER,
            ClassName.ROGUE,
            ClassName.WIZARD,
        ]
        current_step = CharacterCreateView.Step.BASE_ATTRIBUTES_SELECTION
        return {
            "character_create_view-current_step": current_step,
            f"{current_step}-name": f"{fake.name()}",
            f"{current_step}-species": species.name,
            f"{current_step}-klass": fake.random_element(supported_classes),
            f"{current_step}-background": f"{fake.enum(enum_cls=Background)}",
            f"{current_step}-strength": AbilityScore.SCORE_10,
            f"{current_step}-dexterity": AbilityScore.SCORE_12,
            f"{current_step}-constitution": AbilityScore.SCORE_13,
            f"{current_step}-intelligence": AbilityScore.SCORE_14,
            f"{current_step}-wisdom": AbilityScore.SCORE_15,
            f"{current_step}-charisma": AbilityScore.SCORE_8,
            f"{current_step}-gender": f"{fake.enum(enum_cls=Gender)}",
        }

    @pytest.fixture
    def dwarf_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        species = SpeciesFactory(name=SpeciesName.DWARF)
        character_form[f"{current_step}-species"] = species.name
        return character_form

    @pytest.fixture
    def elf_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        species = SpeciesFactory(name=SpeciesName.ELF)
        character_form[f"{current_step}-species"] = species.name
        return character_form

    @pytest.fixture
    def halfling_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        species = SpeciesFactory(name=SpeciesName.HALFLING)
        character_form[f"{current_step}-species"] = species.name
        return character_form

    @pytest.fixture
    def human_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        species = SpeciesFactory(name=SpeciesName.HUMAN)
        character_form[f"{current_step}-species"] = species.name
        return character_form

    @pytest.fixture
    def skills_form(self, character_form):
        fake = Faker()
        klass_key = f"{CharacterCreateView.Step.BASE_ATTRIBUTES_SELECTION}-klass"
        current_step = CharacterCreateView.Step.SKILLS_SELECTION
        skills = fake.random_elements(
            sorted(_get_skills(character_form[klass_key])), length=4, unique=True
        )
        data = {
            "character_create_view-current_step": current_step,
            f"{current_step}-first_skill": skills[0],
            f"{current_step}-second_skill": skills[1],
        }
        if character_form[klass_key] == ClassName.ROGUE:
            data.update(
                {
                    f"{current_step}-third_skill": skills[2],
                    f"{current_step}-fourth_skill": skills[3],
                }
            )
        return data

    @pytest.fixture
    def background_form(self, character_form):
        def _get_random_element(choices):
            fake = Faker()
            choice = fake.random_element(choices)
            # This is necessary to send valid data to the form.
            return (choice[0], choice[0])

        background_key = (
            f"{CharacterCreateView.Step.BASE_ATTRIBUTES_SELECTION}-background"
        )
        current_step = CharacterCreateView.Step.BACKGROUND_COMPLETION
        data = {"character_create_view-current_step": current_step}
        match character_form[background_key]:
            case Background.ACOLYTE:
                data.update(
                    {
                        f"{current_step}-equipment": _get_random_element(
                            _get_holy_symbols()
                        ),
                    }
                )
            case Background.CRIMINAL:
                pass  # Thieves' Tools granted automatically
            case Background.SAGE:
                pass  # Calligrapher's Supplies granted automatically
            case Background.SOLDIER:
                data.update(
                    {
                        f"{current_step}-tool_proficiency": _get_random_element(
                            _get_gaming_set_tools()
                        )
                    }
                )
        return data

    @pytest.fixture
    def equipment_form(self, character_form):
        fake = Faker()
        klass_key = f"{CharacterCreateView.Step.BASE_ATTRIBUTES_SELECTION}-klass"
        current_step = CharacterCreateView.Step.EQUIPMENT_SELECTION
        match character_form[klass_key]:
            case ClassName.CLERIC:
                choices_provider = ClericEquipmentChoicesProvider()
                field_list = ["first_weapon", "second_weapon", "armor", "gear", "pack"]
            case ClassName.FIGHTER:
                choices_provider = FighterEquipmentChoicesProvider()
                field_list = ["first_weapon", "second_weapon", "third_weapon", "pack"]
            case ClassName.ROGUE:
                choices_provider = RogueEquipmentChoicesProvider()
                field_list = ["first_weapon", "second_weapon", "pack"]
            case ClassName.WIZARD:
                choices_provider = WizardEquipmentChoicesProvider()
                field_list = ["first_weapon", "gear", "pack"]
        fields = {}
        if first_weapon_choices := choices_provider.get_first_weapon_choices():
            fields["first_weapon"] = fake.random_element(first_weapon_choices)[1]
        if second_weapon_choices := choices_provider.get_second_weapon_choices():
            fields["second_weapon"] = fake.random_element(second_weapon_choices)[1]
        if third_weapon_choices := choices_provider.get_third_weapon_choices():
            fields["third_weapon"] = fake.random_element(third_weapon_choices)[1]
        if armor_choices := choices_provider.get_armor_choices():
            fields["armor"] = fake.random_element(armor_choices)[1]
        if gear_choices := choices_provider.get_gear_choices():
            fields["gear"] = fake.random_element(gear_choices)[1]
        if pack_choices := choices_provider.get_pack_choices():
            fields["pack"] = fake.random_element(pack_choices)[1]
        data = {"character_create_view-current_step": current_step}
        for field in fields:
            if field in field_list:
                data[f"{current_step}-{field}"] = fields[field]
        return data

    def _create_character(self, client, form_list):
        character = None
        for step, data_step in enumerate(form_list, 1):
            response = client.post((reverse(self.path_name)), data_step)
            if step == len(form_list):
                character = Character.objects.last()
                assertRedirects(response, character.get_absolute_url())
            else:
                assert response.status_code == 200
                # To be sure there is no error at each step.
                assertContains(response, f"Step {step + 1}")
        return character

    def test_character_creation(
        self, client, character_form, skills_form, background_form, equipment_form
    ):
        form_list = [character_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        assert character.name
        assert character.species is not None
        assert character.xp == 0
        assert character.hp >= 100
        assert character.max_hp >= 100
        assert character.hp == character.max_hp

    def test_dwarf_creation(
        self, client, dwarf_form, skills_form, background_form, equipment_form
    ):
        """Test dwarf character creation with D&D 2024 rules (no ability score increases)."""
        form_list = [dwarf_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        # Ability scores are player-chosen in 2024 rules, not species-determined
        assert character.dexterity.score == AbilityScore.SCORE_12
        assert character.constitution.score == AbilityScore.SCORE_13
        assert character.intelligence.score == AbilityScore.SCORE_14
        assert character.charisma.score == AbilityScore.SCORE_8
        # Species-derived attributes
        assert character.species.name == SpeciesName.DWARF
        assert character.speed == 30  # 2024 rules: dwarves have 30 speed

    def test_elf_creation(
        self, client, elf_form, skills_form, background_form, equipment_form
    ):
        """Test elf character creation with D&D 2024 rules (no ability score increases)."""
        form_list = [elf_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        # Ability scores are player-chosen in 2024 rules, not species-determined
        assert character.strength.score == AbilityScore.SCORE_10
        assert character.dexterity.score == AbilityScore.SCORE_12
        assert character.constitution.score == AbilityScore.SCORE_13
        assert character.charisma.score == AbilityScore.SCORE_8
        # Species-derived attributes
        assert character.species.name == SpeciesName.ELF
        assert character.speed == 30

    def test_halfling_creation(
        self, client, halfling_form, skills_form, background_form, equipment_form
    ):
        """Test halfling character creation with D&D 2024 rules (no ability score increases)."""
        form_list = [halfling_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        # Ability scores are player-chosen in 2024 rules, not species-determined
        assert character.strength.score == AbilityScore.SCORE_10
        assert character.dexterity.score == AbilityScore.SCORE_12
        assert character.constitution.score == AbilityScore.SCORE_13
        assert character.intelligence.score == AbilityScore.SCORE_14
        assert character.wisdom.score == AbilityScore.SCORE_15
        assert character.charisma.score == AbilityScore.SCORE_8
        # Species-derived attributes
        assert character.species.name == SpeciesName.HALFLING
        assert character.speed == 30

    def test_human_creation(
        self, client, human_form, skills_form, background_form, equipment_form
    ):
        """Test human character creation with D&D 2024 rules (no ability score increases)."""
        form_list = [human_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        # Ability scores are player-chosen in 2024 rules, not species-determined
        assert character.strength.score == AbilityScore.SCORE_10
        assert character.dexterity.score == AbilityScore.SCORE_12
        assert character.constitution.score == AbilityScore.SCORE_13
        assert character.intelligence.score == AbilityScore.SCORE_14
        assert character.wisdom.score == AbilityScore.SCORE_15
        assert character.charisma.score == AbilityScore.SCORE_8
        # Species-derived attributes
        assert character.species.name == SpeciesName.HUMAN
        assert character.speed == 30

    @pytest.fixture
    def cleric_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        character_form[f"{current_step}-klass"] = ClassName.CLERIC
        return character_form

    def test_cleric_creation(
        self, client, cleric_form, skills_form, background_form, equipment_form
    ):
        form_list = [cleric_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        assert character.hit_dice == "1d8"
        hp = 100 + 8 + character.constitution.modifier
        assert character.hp == hp
        assert set(character.savingthrowproficiency_set.all()) == set(
            SavingThrowProficiency.objects.filter(
                Q(ability_type_id=AbilityName.WISDOM)
                | Q(ability_type_id=AbilityName.CHARISMA)
            )
        )
        assert 100 <= character.inventory.gp <= 250  # Class wealth + 50 GP background
        inventory = character.inventory
        assert inventory.contains(equipment_form["3-first_weapon"])
        assert inventory.contains(equipment_form["3-second_weapon"])
        assert inventory.contains(equipment_form["3-armor"])
        assert inventory.contains(equipment_form["3-gear"])
        assert inventory.contains(equipment_form["3-pack"])
        assert inventory.contains(ArmorName.SHIELD)

    @pytest.fixture
    def fighter_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        character_form[f"{current_step}-klass"] = ClassName.FIGHTER
        return character_form

    def test_fighter_creation(
        self, client, fighter_form, skills_form, background_form, equipment_form
    ):
        form_list = [fighter_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        assert character.hit_dice == "1d10"
        constitution_modifier = character.abilities.get(
            ability_type=AbilityName.CONSTITUTION
        ).modifier
        hp = 100 + 10 + constitution_modifier
        assert character.hp == hp
        assert set(character.savingthrowproficiency_set.all()) == set(
            SavingThrowProficiency.objects.filter(
                Q(ability_type_id=AbilityName.STRENGTH)
                | Q(ability_type_id=AbilityName.CONSTITUTION)
            )
        )
        assert 100 <= character.inventory.gp <= 250  # Class wealth + 50 GP background
        inventory = character.inventory
        # First weapon
        assert (
            inventory.contains(ArmorName.CHAIN_MAIL)
            or inventory.contains(ArmorName.LEATHER)
            and inventory.contains(WeaponName.LONGBOW)
        )
        assert inventory.contains(equipment_form["3-second_weapon"])
        assert inventory.contains(equipment_form["3-third_weapon"])
        assert inventory.contains(equipment_form["3-pack"])

    @pytest.fixture
    def rogue_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        character_form[f"{current_step}-klass"] = ClassName.ROGUE
        return character_form

    def test_rogue_creation(
        self, client, rogue_form, skills_form, background_form, equipment_form
    ):
        form_list = [rogue_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        assert character.hit_dice == "1d8"
        constitution_modifier = character.abilities.get(
            ability_type=AbilityName.CONSTITUTION
        ).modifier
        hp = 100 + 8 + constitution_modifier
        assert character.hp == hp
        assert set(character.savingthrowproficiency_set.all()) == set(
            SavingThrowProficiency.objects.filter(
                Q(ability_type_id=AbilityName.DEXTERITY)
                | Q(ability_type_id=AbilityName.INTELLIGENCE)
            )
        )
        assert 90 <= character.inventory.gp <= 210  # Class wealth + 50 GP background
        inventory = character.inventory
        assert inventory.contains(equipment_form["3-first_weapon"])
        assert inventory.contains(equipment_form["3-second_weapon"])
        assert inventory.contains(equipment_form["3-pack"])
        assert inventory.contains(ArmorName.LEATHER)
        assert inventory.contains(WeaponName.DAGGER, 2)
        assert inventory.contains(ToolName.THIEVES_TOOLS)

    @pytest.fixture
    def wizard_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        character_form[f"{current_step}-klass"] = ClassName.WIZARD
        return character_form

    def test_wizard_creation(
        self, client, wizard_form, skills_form, background_form, equipment_form
    ):
        form_list = [wizard_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        assert character.hit_dice == "1d6"
        constitution_modifier = character.abilities.get(
            ability_type=AbilityName.CONSTITUTION
        ).modifier
        hp = 100 + 6 + constitution_modifier
        assert character.hp == hp
        assert set(character.savingthrowproficiency_set.all()) == set(
            SavingThrowProficiency.objects.filter(
                Q(ability_type_id=AbilityName.INTELLIGENCE)
                | Q(ability_type_id=AbilityName.WISDOM)
            )
        )
        assert 90 <= character.inventory.gp <= 210  # Class wealth + 50 GP background
        inventory = character.inventory
        assert inventory.contains(equipment_form["3-first_weapon"])
        assert inventory.contains(equipment_form["3-gear"])
        assert inventory.contains(equipment_form["3-pack"])
        assert inventory.contains(GearName.SPELLBOOK)

    @pytest.fixture
    def acolyte_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        character_form[f"{current_step}-background"] = Background.ACOLYTE
        return character_form

    def test_acolyte_creation(
        self, client, acolyte_form, skills_form, background_form, equipment_form
    ):
        form_list = [acolyte_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        SkillProficiency.objects.filter(
            Q(character=character, skill=Skill.objects.get(name=SkillName.INSIGHT))
            | Q(character=character, skill=Skill.objects.get(name=SkillName.RELIGION))
        )
        assert (
            character.personality_trait
            in BACKGROUNDS[Background.ACOLYTE]["personality_traits"].values()
        )
        assert character.ideal in BACKGROUNDS[Background.ACOLYTE]["ideals"].values()
        assert character.bond in BACKGROUNDS[Background.ACOLYTE]["bonds"].values()
        assert character.flaw in BACKGROUNDS[Background.ACOLYTE]["flaws"].values()

    @pytest.fixture
    def criminal_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        character_form[f"{current_step}-background"] = Background.CRIMINAL
        return character_form

    def test_criminal_creation(
        self, client, criminal_form, skills_form, background_form, equipment_form
    ):
        form_list = [criminal_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        SkillProficiency.objects.filter(
            Q(
                character=character,
                skill=Skill.objects.get(name=SkillName.SLEIGHT_OF_HAND),
            )
            | Q(character=character, skill=Skill.objects.get(name=SkillName.STEALTH))
        )
        assert (
            character.personality_trait
            in BACKGROUNDS[Background.CRIMINAL]["personality_traits"].values()
        )
        assert character.ideal in BACKGROUNDS[Background.CRIMINAL]["ideals"].values()
        assert character.bond in BACKGROUNDS[Background.CRIMINAL]["bonds"].values()
        assert character.flaw in BACKGROUNDS[Background.CRIMINAL]["flaws"].values()

    @pytest.fixture
    def sage_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        character_form[f"{current_step}-background"] = Background.SAGE
        return character_form

    def test_sage_creation(
        self, client, sage_form, skills_form, background_form, equipment_form
    ):
        form_list = [sage_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        SkillProficiency.objects.filter(
            Q(character=character, skill=Skill.objects.get(name=SkillName.ARCANA))
            | Q(character=character, skill=Skill.objects.get(name=SkillName.HISTORY))
        )
        assert (
            character.personality_trait
            in BACKGROUNDS[Background.SAGE]["personality_traits"].values()
        )
        assert character.ideal in BACKGROUNDS[Background.SAGE]["ideals"].values()
        assert character.bond in BACKGROUNDS[Background.SAGE]["bonds"].values()
        assert character.flaw in BACKGROUNDS[Background.SAGE]["flaws"].values()

    @pytest.fixture
    def soldier_form(self, character_form):
        current_step = character_form["character_create_view-current_step"]
        character_form[f"{current_step}-background"] = Background.SOLDIER
        return character_form

    def test_soldier_creation(
        self, client, soldier_form, skills_form, background_form, equipment_form
    ):
        form_list = [soldier_form, skills_form, background_form, equipment_form]
        character = self._create_character(client, form_list)
        SkillProficiency.objects.filter(
            Q(character=character, skill=Skill.objects.get(name=SkillName.ATHLETICS))
            | Q(
                character=character,
                skill=Skill.objects.get(name=SkillName.INTIMIDATION),
            )
        )
        assert (
            character.personality_trait
            in BACKGROUNDS[Background.SOLDIER]["personality_traits"].values()
        )
        assert character.ideal in BACKGROUNDS[Background.SOLDIER]["ideals"].values()
        assert character.bond in BACKGROUNDS[Background.SOLDIER]["bonds"].values()
        assert character.flaw in BACKGROUNDS[Background.SOLDIER]["flaws"].values()
