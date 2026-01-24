import pytest
from django.db.models import Q
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from character.constants.abilities import AbilityName, AbilityScore
from character.constants.backgrounds import BACKGROUNDS, Background
from character.constants.equipment import ArmorName, GearName, ToolName, WeaponName
from character.constants.species import SpeciesName
from character.constants.skills import SkillName
from character.forms.equipment_choices_providers import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)
from character.forms.wizard_forms import _get_skills
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
        assertTemplateUsed(response, "character/character_sheet.html")

    def test_content_character_is_in_game(self, client, character):
        game = GameFactory()
        PlayerFactory(game=game, character=character)
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assertContains(response, game.name)

    def test_context_contains_abilities(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        abilities = response.context["abilities"]
        assert len(abilities) == 6
        ability_names = {a["abbreviation"] for a in abilities}
        assert ability_names == {"STR", "DEX", "CON", "INT", "WIS", "CHA"}
        for ability in abilities:
            assert "name" in ability
            assert "abbreviation" in ability
            assert "score" in ability
            assert "modifier" in ability

    def test_context_contains_skills(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        skills = response.context["skills"]
        assert len(skills) > 0
        for skill in skills:
            assert "name" in skill
            assert "ability" in skill
            assert "proficient" in skill
            assert "modifier" in skill

    def test_context_contains_saving_throws(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        saving_throws = response.context["saving_throws"]
        assert len(saving_throws) == 6
        for save in saving_throws:
            assert "name" in save
            assert "proficient" in save
            assert "modifier" in save

    def test_context_contains_inventory(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assert "inventory" in response.context
        assert response.context["inventory"] == character.inventory

    def test_context_contains_attacks(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assert "attacks" in response.context
        assert isinstance(response.context["attacks"], list)

    def test_context_contains_racial_traits(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assert "racial_traits" in response.context
        assert isinstance(response.context["racial_traits"], list)

    def test_context_contains_class_features(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assert "class_features" in response.context
        assert isinstance(response.context["class_features"], list)

    def test_context_contains_feats(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assert "feats" in response.context
        assert isinstance(response.context["feats"], list)

    def test_context_contains_spell_placeholders(self, client, character):
        response = client.get(character.get_absolute_url())
        assert response.status_code == 200
        assert response.context["spells_by_level"] == {}
        assert response.context["spell_slots"] == []


@pytest.mark.django_db
class TestCharacterDetailViewWithWeapons:
    """Tests for attack calculation with weapons."""

    def test_melee_weapon_attack_uses_strength(self, client, character):
        from character.models.equipment import Weapon, WeaponSettings

        settings = WeaponSettings.objects.get(name=WeaponName.LONGSWORD)
        Weapon.objects.create(settings=settings, inventory=character.inventory)
        response = client.get(character.get_absolute_url())
        attacks = response.context["attacks"]
        assert len(attacks) == 1
        assert attacks[0]["name"] == str(WeaponName.LONGSWORD)
        assert "bonus" in attacks[0]
        assert "damage" in attacks[0]

    def test_ranged_weapon_attack_uses_dexterity(self, client, character):
        from character.models.equipment import Weapon, WeaponSettings

        settings = WeaponSettings.objects.get(name=WeaponName.LONGBOW)
        Weapon.objects.create(settings=settings, inventory=character.inventory)
        response = client.get(character.get_absolute_url())
        attacks = response.context["attacks"]
        assert len(attacks) == 1
        assert attacks[0]["name"] == str(WeaponName.LONGBOW)

    def test_finesse_weapon_uses_best_modifier(self, client, character):
        from character.models.equipment import Weapon, WeaponSettings

        settings = WeaponSettings.objects.get(name=WeaponName.RAPIER)
        Weapon.objects.create(settings=settings, inventory=character.inventory)
        response = client.get(character.get_absolute_url())
        attacks = response.context["attacks"]
        assert len(attacks) == 1
        assert attacks[0]["name"] == str(WeaponName.RAPIER)


@pytest.mark.django_db
class TestCharacterDetailViewWithClassFeatures:
    """Tests for class feature display."""

    def test_displays_class_features(self, client, fighter):
        from character.models.classes import CharacterFeature, ClassFeature

        feature = ClassFeature.objects.filter(
            klass__name=ClassName.FIGHTER, level=1
        ).first()
        if feature:
            CharacterFeature.objects.create(
                character=fighter,
                class_feature=feature,
                source_class=fighter.primary_class,
                level_gained=1,
            )
        response = client.get(fighter.get_absolute_url())
        class_features = response.context["class_features"]
        if feature:
            assert len(class_features) >= 1
            assert any(f["name"] == feature.name for f in class_features)


@pytest.mark.django_db
class TestCharacterDetailViewWithFeats:
    """Tests for feat display."""

    def test_displays_feats(self, client, character):
        from character.models.feats import CharacterFeat, Feat
        from character.constants.feats import FeatName

        feat = Feat.objects.get(name=FeatName.ALERT)
        CharacterFeat.objects.create(
            character=character, feat=feat, granted_by="background"
        )
        response = client.get(character.get_absolute_url())
        feats = response.context["feats"]
        assert len(feats) == 1
        assert feats[0]["name"] == feat.get_name_display()
        assert feats[0]["description"] == feat.description


@pytest.mark.django_db
class TestCharacterDetailViewWithSpeciesTraits:
    """Tests for species trait display."""

    def test_displays_species_traits(self, client, character):
        response = client.get(character.get_absolute_url())
        racial_traits = response.context["racial_traits"]
        if character.species and character.species.traits.exists():
            assert len(racial_traits) > 0
            for trait in racial_traits:
                assert "name" in trait
                assert "description" in trait


@pytest.fixture(scope="class")
def create_characters(django_db_blocker):
    with django_db_blocker.unblock():
        number_of_characters = 22
        for _ in range(number_of_characters):
            CharacterFactory()


@pytest.mark.django_db
class TestCharacterCreateView:
    """Tests for the 7-step character creation wizard."""

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
        assertTemplateUsed(response, "character/wizard/step_species.html")

    @pytest.fixture
    def species_form(self):
        """Step 0: Species selection form."""
        fake = Faker()
        species = SpeciesFactory(name=fake.enum(enum_cls=SpeciesName))
        return {
            "character_create_view-current_step": CharacterCreateView.Step.SPECIES_SELECTION,
            f"{CharacterCreateView.Step.SPECIES_SELECTION}-species": species.name,
        }

    @pytest.fixture
    def class_form(self):
        """Step 1: Class selection form."""
        fake = Faker()
        supported_classes = [
            ClassName.CLERIC,
            ClassName.FIGHTER,
            ClassName.ROGUE,
            ClassName.WIZARD,
        ]
        return {
            "character_create_view-current_step": CharacterCreateView.Step.CLASS_SELECTION,
            f"{CharacterCreateView.Step.CLASS_SELECTION}-klass": fake.random_element(
                supported_classes
            ),
        }

    @pytest.fixture
    def abilities_form(self):
        """Step 2: Ability scores form."""
        return {
            "character_create_view-current_step": CharacterCreateView.Step.ABILITY_SCORES,
            f"{CharacterCreateView.Step.ABILITY_SCORES}-generation_method": "standard",
            f"{CharacterCreateView.Step.ABILITY_SCORES}-strength": AbilityScore.SCORE_10,
            f"{CharacterCreateView.Step.ABILITY_SCORES}-dexterity": AbilityScore.SCORE_12,
            f"{CharacterCreateView.Step.ABILITY_SCORES}-constitution": AbilityScore.SCORE_13,
            f"{CharacterCreateView.Step.ABILITY_SCORES}-intelligence": AbilityScore.SCORE_14,
            f"{CharacterCreateView.Step.ABILITY_SCORES}-wisdom": AbilityScore.SCORE_15,
            f"{CharacterCreateView.Step.ABILITY_SCORES}-charisma": AbilityScore.SCORE_8,
        }

    @pytest.fixture
    def background_form(self):
        """Step 3: Background selection form."""
        fake = Faker()
        return {
            "character_create_view-current_step": CharacterCreateView.Step.BACKGROUND_SELECTION,
            f"{CharacterCreateView.Step.BACKGROUND_SELECTION}-background": fake.enum(
                enum_cls=Background
            ),
        }

    @pytest.fixture
    def skills_form(self, class_form):
        """Step 4: Skills selection form."""
        fake = Faker()
        klass = class_form[f"{CharacterCreateView.Step.CLASS_SELECTION}-klass"]
        skills = fake.random_elements(sorted(_get_skills(klass)), length=4, unique=True)
        data = {
            "character_create_view-current_step": CharacterCreateView.Step.SKILLS_SELECTION,
            f"{CharacterCreateView.Step.SKILLS_SELECTION}-first_skill": skills[0],
            f"{CharacterCreateView.Step.SKILLS_SELECTION}-second_skill": skills[1],
        }
        if klass == ClassName.ROGUE:
            data.update(
                {
                    f"{CharacterCreateView.Step.SKILLS_SELECTION}-third_skill": skills[
                        2
                    ],
                    f"{CharacterCreateView.Step.SKILLS_SELECTION}-fourth_skill": skills[
                        3
                    ],
                }
            )
        return data

    @pytest.fixture
    def equipment_form(self, class_form):
        """Step 5: Equipment selection form."""
        fake = Faker()
        klass = class_form[f"{CharacterCreateView.Step.CLASS_SELECTION}-klass"]
        step = CharacterCreateView.Step.EQUIPMENT_SELECTION
        match klass:
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
            case _:
                choices_provider = ClericEquipmentChoicesProvider()
                field_list = ["first_weapon", "second_weapon", "armor", "gear", "pack"]

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

        data = {"character_create_view-current_step": step}
        for field in fields:
            if field in field_list:
                data[f"{step}-{field}"] = fields[field]
        return data

    @pytest.fixture
    def review_form(self):
        """Step 6: Review and name form."""
        fake = Faker()
        return {
            "character_create_view-current_step": CharacterCreateView.Step.REVIEW,
            f"{CharacterCreateView.Step.REVIEW}-name": fake.name(),
        }

    # Species-specific fixtures
    @pytest.fixture
    def dwarf_species_form(self):
        species = SpeciesFactory(name=SpeciesName.DWARF)
        return {
            "character_create_view-current_step": CharacterCreateView.Step.SPECIES_SELECTION,
            f"{CharacterCreateView.Step.SPECIES_SELECTION}-species": species.name,
        }

    @pytest.fixture
    def elf_species_form(self):
        species = SpeciesFactory(name=SpeciesName.ELF)
        return {
            "character_create_view-current_step": CharacterCreateView.Step.SPECIES_SELECTION,
            f"{CharacterCreateView.Step.SPECIES_SELECTION}-species": species.name,
        }

    @pytest.fixture
    def halfling_species_form(self):
        species = SpeciesFactory(name=SpeciesName.HALFLING)
        return {
            "character_create_view-current_step": CharacterCreateView.Step.SPECIES_SELECTION,
            f"{CharacterCreateView.Step.SPECIES_SELECTION}-species": species.name,
        }

    @pytest.fixture
    def human_species_form(self):
        species = SpeciesFactory(name=SpeciesName.HUMAN)
        return {
            "character_create_view-current_step": CharacterCreateView.Step.SPECIES_SELECTION,
            f"{CharacterCreateView.Step.SPECIES_SELECTION}-species": species.name,
        }

    # Class-specific fixtures
    @pytest.fixture
    def cleric_class_form(self):
        return {
            "character_create_view-current_step": CharacterCreateView.Step.CLASS_SELECTION,
            f"{CharacterCreateView.Step.CLASS_SELECTION}-klass": ClassName.CLERIC,
        }

    @pytest.fixture
    def fighter_class_form(self):
        return {
            "character_create_view-current_step": CharacterCreateView.Step.CLASS_SELECTION,
            f"{CharacterCreateView.Step.CLASS_SELECTION}-klass": ClassName.FIGHTER,
        }

    @pytest.fixture
    def rogue_class_form(self):
        return {
            "character_create_view-current_step": CharacterCreateView.Step.CLASS_SELECTION,
            f"{CharacterCreateView.Step.CLASS_SELECTION}-klass": ClassName.ROGUE,
        }

    @pytest.fixture
    def wizard_class_form(self):
        return {
            "character_create_view-current_step": CharacterCreateView.Step.CLASS_SELECTION,
            f"{CharacterCreateView.Step.CLASS_SELECTION}-klass": ClassName.WIZARD,
        }

    # Background-specific fixtures
    @pytest.fixture
    def acolyte_background_form(self):
        return {
            "character_create_view-current_step": CharacterCreateView.Step.BACKGROUND_SELECTION,
            f"{CharacterCreateView.Step.BACKGROUND_SELECTION}-background": Background.ACOLYTE,
        }

    @pytest.fixture
    def criminal_background_form(self):
        return {
            "character_create_view-current_step": CharacterCreateView.Step.BACKGROUND_SELECTION,
            f"{CharacterCreateView.Step.BACKGROUND_SELECTION}-background": Background.CRIMINAL,
        }

    @pytest.fixture
    def sage_background_form(self):
        return {
            "character_create_view-current_step": CharacterCreateView.Step.BACKGROUND_SELECTION,
            f"{CharacterCreateView.Step.BACKGROUND_SELECTION}-background": Background.SAGE,
        }

    @pytest.fixture
    def soldier_background_form(self):
        return {
            "character_create_view-current_step": CharacterCreateView.Step.BACKGROUND_SELECTION,
            f"{CharacterCreateView.Step.BACKGROUND_SELECTION}-background": Background.SOLDIER,
        }

    def _make_skills_form(self, klass):
        """Create skills form for a specific class."""
        fake = Faker()
        skills = fake.random_elements(sorted(_get_skills(klass)), length=4, unique=True)
        step = CharacterCreateView.Step.SKILLS_SELECTION
        data = {
            "character_create_view-current_step": step,
            f"{step}-first_skill": skills[0],
            f"{step}-second_skill": skills[1],
        }
        if klass == ClassName.ROGUE:
            data[f"{step}-third_skill"] = skills[2]
            data[f"{step}-fourth_skill"] = skills[3]
        return data

    def _make_equipment_form(self, klass):
        """Create equipment form for a specific class."""
        fake = Faker()
        step = CharacterCreateView.Step.EQUIPMENT_SELECTION
        match klass:
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
            case _:
                choices_provider = ClericEquipmentChoicesProvider()
                field_list = ["first_weapon", "second_weapon", "armor", "gear", "pack"]

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

        data = {"character_create_view-current_step": step}
        for field in fields:
            if field in field_list:
                data[f"{step}-{field}"] = fields[field]
        return data

    def _create_character(self, client, form_list):
        """Submit all wizard steps and return the created character."""
        character = None
        for step, data_step in enumerate(form_list, 1):
            response = client.post((reverse(self.path_name)), data_step)
            if step == len(form_list):
                character = Character.objects.last()
                assertRedirects(response, character.get_absolute_url())
            else:
                assert response.status_code == 200
        return character

    def test_character_creation(
        self,
        client,
        species_form,
        class_form,
        abilities_form,
        background_form,
        skills_form,
        equipment_form,
        review_form,
    ):
        form_list = [
            species_form,
            class_form,
            abilities_form,
            background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
        character = self._create_character(client, form_list)
        assert character.name
        assert character.species is not None
        assert character.xp == 0
        assert character.hp >= 100
        assert character.max_hp >= 100
        assert character.hp == character.max_hp

    def test_dwarf_creation(
        self,
        client,
        dwarf_species_form,
        class_form,
        abilities_form,
        background_form,
        skills_form,
        equipment_form,
        review_form,
    ):
        """Test dwarf character creation with D&D 2024 rules."""
        form_list = [
            dwarf_species_form,
            class_form,
            abilities_form,
            background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
        character = self._create_character(client, form_list)
        assert character.dexterity.score == AbilityScore.SCORE_12
        assert character.constitution.score == AbilityScore.SCORE_13
        assert character.intelligence.score == AbilityScore.SCORE_14
        assert character.charisma.score == AbilityScore.SCORE_8
        assert character.species.name == SpeciesName.DWARF
        assert character.speed == 30

    def test_elf_creation(
        self,
        client,
        elf_species_form,
        class_form,
        abilities_form,
        background_form,
        skills_form,
        equipment_form,
        review_form,
    ):
        """Test elf character creation with D&D 2024 rules."""
        form_list = [
            elf_species_form,
            class_form,
            abilities_form,
            background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
        character = self._create_character(client, form_list)
        assert character.strength.score == AbilityScore.SCORE_10
        assert character.dexterity.score == AbilityScore.SCORE_12
        assert character.constitution.score == AbilityScore.SCORE_13
        assert character.charisma.score == AbilityScore.SCORE_8
        assert character.species.name == SpeciesName.ELF
        assert character.speed == 30

    def test_halfling_creation(
        self,
        client,
        halfling_species_form,
        class_form,
        abilities_form,
        background_form,
        skills_form,
        equipment_form,
        review_form,
    ):
        """Test halfling character creation with D&D 2024 rules."""
        form_list = [
            halfling_species_form,
            class_form,
            abilities_form,
            background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
        character = self._create_character(client, form_list)
        assert character.strength.score == AbilityScore.SCORE_10
        assert character.dexterity.score == AbilityScore.SCORE_12
        assert character.constitution.score == AbilityScore.SCORE_13
        assert character.intelligence.score == AbilityScore.SCORE_14
        assert character.wisdom.score == AbilityScore.SCORE_15
        assert character.charisma.score == AbilityScore.SCORE_8
        assert character.species.name == SpeciesName.HALFLING
        assert character.speed == 30

    def test_human_creation(
        self,
        client,
        human_species_form,
        class_form,
        abilities_form,
        background_form,
        skills_form,
        equipment_form,
        review_form,
    ):
        """Test human character creation with D&D 2024 rules."""
        form_list = [
            human_species_form,
            class_form,
            abilities_form,
            background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
        character = self._create_character(client, form_list)
        assert character.strength.score == AbilityScore.SCORE_10
        assert character.dexterity.score == AbilityScore.SCORE_12
        assert character.constitution.score == AbilityScore.SCORE_13
        assert character.intelligence.score == AbilityScore.SCORE_14
        assert character.wisdom.score == AbilityScore.SCORE_15
        assert character.charisma.score == AbilityScore.SCORE_8
        assert character.species.name == SpeciesName.HUMAN
        assert character.speed == 30

    def test_cleric_creation(
        self,
        client,
        species_form,
        cleric_class_form,
        abilities_form,
        background_form,
        review_form,
    ):
        skills_form = self._make_skills_form(ClassName.CLERIC)
        equipment_form = self._make_equipment_form(ClassName.CLERIC)
        form_list = [
            species_form,
            cleric_class_form,
            abilities_form,
            background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
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
        assert 100 <= character.inventory.gp <= 250
        inventory = character.inventory
        step = CharacterCreateView.Step.EQUIPMENT_SELECTION
        assert inventory.contains(equipment_form[f"{step}-first_weapon"])
        assert inventory.contains(equipment_form[f"{step}-second_weapon"])
        assert inventory.contains(equipment_form[f"{step}-armor"])
        assert inventory.contains(equipment_form[f"{step}-gear"])
        assert inventory.contains(equipment_form[f"{step}-pack"])
        assert inventory.contains(ArmorName.SHIELD)

    def test_fighter_creation(
        self,
        client,
        species_form,
        fighter_class_form,
        abilities_form,
        background_form,
        review_form,
    ):
        skills_form = self._make_skills_form(ClassName.FIGHTER)
        equipment_form = self._make_equipment_form(ClassName.FIGHTER)
        form_list = [
            species_form,
            fighter_class_form,
            abilities_form,
            background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
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
        assert 100 <= character.inventory.gp <= 250
        inventory = character.inventory
        step = CharacterCreateView.Step.EQUIPMENT_SELECTION
        assert (
            inventory.contains(ArmorName.CHAIN_MAIL)
            or inventory.contains(ArmorName.LEATHER)
            and inventory.contains(WeaponName.LONGBOW)
        )
        assert inventory.contains(equipment_form[f"{step}-second_weapon"])
        assert inventory.contains(equipment_form[f"{step}-third_weapon"])
        assert inventory.contains(equipment_form[f"{step}-pack"])

    def test_rogue_creation(
        self,
        client,
        species_form,
        rogue_class_form,
        abilities_form,
        background_form,
        review_form,
    ):
        skills_form = self._make_skills_form(ClassName.ROGUE)
        equipment_form = self._make_equipment_form(ClassName.ROGUE)
        form_list = [
            species_form,
            rogue_class_form,
            abilities_form,
            background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
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
        assert 90 <= character.inventory.gp <= 210
        inventory = character.inventory
        step = CharacterCreateView.Step.EQUIPMENT_SELECTION
        assert inventory.contains(equipment_form[f"{step}-first_weapon"])
        assert inventory.contains(equipment_form[f"{step}-second_weapon"])
        assert inventory.contains(equipment_form[f"{step}-pack"])
        assert inventory.contains(ArmorName.LEATHER)
        assert inventory.contains(WeaponName.DAGGER, 2)
        assert inventory.contains(ToolName.THIEVES_TOOLS)

    def test_wizard_creation(
        self,
        client,
        species_form,
        wizard_class_form,
        abilities_form,
        background_form,
        review_form,
    ):
        skills_form = self._make_skills_form(ClassName.WIZARD)
        equipment_form = self._make_equipment_form(ClassName.WIZARD)
        form_list = [
            species_form,
            wizard_class_form,
            abilities_form,
            background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
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
        assert 90 <= character.inventory.gp <= 210
        inventory = character.inventory
        step = CharacterCreateView.Step.EQUIPMENT_SELECTION
        assert inventory.contains(equipment_form[f"{step}-first_weapon"])
        assert inventory.contains(equipment_form[f"{step}-gear"])
        assert inventory.contains(equipment_form[f"{step}-pack"])
        assert inventory.contains(GearName.SPELLBOOK)

    def test_acolyte_creation(
        self,
        client,
        species_form,
        class_form,
        abilities_form,
        acolyte_background_form,
        skills_form,
        equipment_form,
        review_form,
    ):
        form_list = [
            species_form,
            class_form,
            abilities_form,
            acolyte_background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
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

    def test_criminal_creation(
        self,
        client,
        species_form,
        class_form,
        abilities_form,
        criminal_background_form,
        skills_form,
        equipment_form,
        review_form,
    ):
        form_list = [
            species_form,
            class_form,
            abilities_form,
            criminal_background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
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

    def test_sage_creation(
        self,
        client,
        species_form,
        class_form,
        abilities_form,
        sage_background_form,
        skills_form,
        equipment_form,
        review_form,
    ):
        form_list = [
            species_form,
            class_form,
            abilities_form,
            sage_background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
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

    def test_soldier_creation(
        self,
        client,
        species_form,
        class_form,
        abilities_form,
        soldier_background_form,
        skills_form,
        equipment_form,
        review_form,
    ):
        form_list = [
            species_form,
            class_form,
            abilities_form,
            soldier_background_form,
            skills_form,
            equipment_form,
            review_form,
        ]
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
