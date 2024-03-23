import pytest
from django.db.models import Q
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from character.constants.abilities import AbilityName
from character.constants.backgrounds import BACKGROUNDS, Background
from character.constants.character import Gender
from character.constants.races import LanguageName, Race, SenseName
from character.constants.skills import SkillName
from character.forms.character import CharacterCreateForm
from character.models.character import Character
from character.models.klasses import Klass
from character.models.proficiencies import SavingThrowProficiency, SkillProficiency
from character.models.skills import Skill
from character.models.races import Language, Sense
from character.utils.abilities import AbilityScore
from character.views.character import (
    CharacterCreateView,
    CharacterDetailView,
    CharacterListView,
)
from game.tests.factories import GameFactory, PlayerFactory
from utils.factories import UserFactory

from ..factories import CharacterFactory


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
class TestCharacterListView:
    path_name = "character-list"

    def test_view_mapping(self, client, character):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterListView

    def test_template_mapping(self, client, character):
        response = client.get(reverse(self.path_name))
        assertTemplateUsed(response, "character/character_list.html")

    def test_pagination_size(self, client, character, create_characters):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 20

    def test_pagination_size_next_page(self, client, character, create_characters):
        response = client.get(reverse(self.path_name) + "?page=2")
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 3

    def test_ordering(self, client, character, create_characters):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        xp = 0
        for c in response.context["character_list"]:
            if xp == 0:
                xp = c.xp
            else:
                assert xp >= c.xp
                xp = c.xp

    @pytest.fixture
    def delete_characters(self):
        Character.objects.all().delete()

    def test_content_no_existing_character(self, client, character, delete_characters):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertContains(response, "There is no character available...")

    def test_content_character_is_in_game(self, client, character, delete_characters):
        # The idea is to have only one character. Assign them to a game, and check that
        # game name is part of the page content.
        game = GameFactory()
        PlayerFactory(game=game)
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertContains(response, game.name)


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
        return {
            "name": f"{fake.name()}",
            "race": f"{fake.enum(enum_cls=Race)}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }

    def test_character_creation_common(self, client, character_form):
        form = CharacterCreateForm(character_form)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        assert character.name, form.cleaned_data["name"]
        assert character.race, form.cleaned_data["race"]
        assert character.xp == 0
        assert character.hp >= 100
        assert character.max_hp >= 100
        assert character.hp == character.max_hp

    @pytest.fixture
    def dwarf_form(self):
        fake = Faker()
        return {
            "name": f"{fake.name()}",
            "race": f"{fake.random_element(elements=(Race.HILL_DWARF, Race.MOUNTAIN_DWARF))}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }

    def test_character_creation_dwarf(self, client, dwarf_form):
        form = CharacterCreateForm(dwarf_form)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        dexterity = character.abilities.get(ability_type=AbilityName.DEXTERITY).score
        assert dexterity == AbilityScore.SCORE_12

        constitution = character.abilities.get(
            ability_type=AbilityName.CONSTITUTION
        ).score
        assert constitution == AbilityScore.SCORE_13 + 2

        intelligence = character.abilities.get(
            ability_type=AbilityName.INTELLIGENCE
        ).score
        assert intelligence == AbilityScore.SCORE_14

        charisma = character.abilities.get(ability_type=AbilityName.CHARISMA).score
        assert charisma == AbilityScore.SCORE_8

        assert character.speed == 25

        languages = set()
        languages.add(Language.objects.get(name=LanguageName.COMMON))
        languages.add(Language.objects.get(name=LanguageName.DWARVISH))
        assert set(character.languages.all()) == languages

        senses = set()
        senses.add(Sense.objects.get(name=SenseName.DARKVISION))
        senses.add(Sense.objects.get(name=SenseName.DWARVEN_RESILIENCE))
        senses.add(Sense.objects.get(name=SenseName.DWARVEN_COMBAT_TRAINING))
        senses.add(Sense.objects.get(name=SenseName.TOOL_PROFICIENCY))
        senses.add(Sense.objects.get(name=SenseName.STONECUNNING))
        assert senses.issubset(set(character.senses.all()))

    @pytest.fixture
    def hill_dwarf_form(self):
        fake = Faker()
        return {
            "name": f"{fake.name()}",
            "race": f"{Race.HILL_DWARF}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }

    def test_character_creation_hill_dwarf(self, client, hill_dwarf_form):
        form = CharacterCreateForm(hill_dwarf_form)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        assert 3.8 < character.height <= 3.8 + 2 * 4 / 12
        assert 115 < character.weight <= 115 + 2 * 6 * 12

        wisdom = character.abilities.get(ability_type=AbilityName.WISDOM).score
        assert wisdom == AbilityScore.SCORE_15 + 1

        assert character.senses.get(name=SenseName.DWARVEN_TOUGHNESS)

    @pytest.fixture
    def moutain_dwarf_form(self):
        fake = Faker()
        return {
            "name": f"{fake.name()}",
            "race": f"{Race.MOUNTAIN_DWARF}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }

    def test_character_creation_mountain_dwarf(self, client, moutain_dwarf_form):
        form = CharacterCreateForm(moutain_dwarf_form)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        assert 4 < character.height <= 4 + 2 * 4 / 12
        assert 130 < character.weight <= 130 + 2 * 6 * 12

        strength = character.abilities.get(ability_type=AbilityName.STRENGTH).score
        assert strength == AbilityScore.SCORE_10 + 2

        assert character.senses.get(name=SenseName.DWARVEN_ARMOR_TRAINING)

    @pytest.fixture
    def elf_form(self):
        fake = Faker()
        return {
            "name": f"{fake.name()}",
            "race": f"{fake.random_element(elements=(Race.HIGH_ELF, Race.WOOD_ELF))}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }

    def test_character_creation_elf(self, client, elf_form):
        form = CharacterCreateForm(elf_form)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code, 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        strength = character.abilities.get(ability_type=AbilityName.STRENGTH).score
        assert strength == AbilityScore.SCORE_10

        dexterity = character.abilities.get(ability_type=AbilityName.DEXTERITY).score
        assert dexterity == AbilityScore.SCORE_12 + 2

        constitution = character.abilities.get(
            ability_type=AbilityName.CONSTITUTION
        ).score
        assert constitution == AbilityScore.SCORE_13

        charisma = character.abilities.get(ability_type=AbilityName.CHARISMA).score
        assert charisma == AbilityScore.SCORE_8

        assert character.speed == 30

        languages = set()
        languages.add(Language.objects.get(name=LanguageName.COMMON))
        languages.add(Language.objects.get(name=LanguageName.ELVISH))
        assert set(character.languages.all()) == languages

        senses = set()
        senses.add(Sense.objects.get(name=SenseName.DARKVISION))
        senses.add(Sense.objects.get(name=SenseName.KEEN_SENSES))
        senses.add(Sense.objects.get(name=SenseName.FEY_ANCESTRY))
        senses.add(Sense.objects.get(name=SenseName.TRANCE))
        assert senses.issubset(set(character.senses.all()))

    @pytest.fixture
    def high_elf_form(self):
        fake = Faker()
        return {
            "name": f"{fake.name()}",
            "race": f"{Race.HIGH_ELF}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }

    def test_character_creation_high_elf(self, client, high_elf_form):
        form = CharacterCreateForm(high_elf_form)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code, 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        assert 4.6 < character.height <= 4.6 + 2 * 10 / 12
        assert 90 < character.weight <= 90 + 1 * 4 * 12

        intelligence = character.abilities.get(
            ability_type=AbilityName.INTELLIGENCE
        ).score
        assert intelligence == AbilityScore.SCORE_14 + 1

        assert character.senses.get(name=SenseName.ELF_WEAPON_TRAINING)
        assert character.senses.get(name=SenseName.CANTRIP)
        assert character.senses.get(name=SenseName.EXTRA_LANGUAGE)

    @pytest.fixture
    def wood_elf_form(self):
        fake = Faker()
        return {
            "name": f"{fake.name()}",
            "race": f"{Race.WOOD_ELF}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }

    def test_character_creation_wood_elf(self, client, wood_elf_form):
        form = CharacterCreateForm(wood_elf_form)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code, 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        assert 4.6 < character.height <= 4.6 + 2 * 10 / 12
        assert 100 < character.weight <= 100 + 1 * 4 * 12

        wisdom = character.abilities.get(ability_type=AbilityName.WISDOM).score
        assert wisdom == AbilityScore.SCORE_15 + 1

        assert character.senses.get(name=SenseName.ELF_WEAPON_TRAINING)
        assert character.senses.get(name=SenseName.FLEET_OF_FOOT)
        assert character.senses.get(name=SenseName.MASK_OF_THE_WILD)

    @pytest.fixture
    def halfling_form(self):
        fake = Faker()
        return {
            "name": f"{fake.name()}",
            "race": f"{Race.HALFLING}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }

    def test_character_creation_halfling(self, client, halfling_form):
        form = CharacterCreateForm(halfling_form)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        assert 2.7 < character.height <= 2.7 + 2 * 4 / 12
        assert 35 == character.weight

        strength = character.abilities.get(ability_type=AbilityName.STRENGTH).score
        assert strength == AbilityScore.SCORE_10

        dexterity = character.abilities.get(ability_type=AbilityName.DEXTERITY).score
        assert dexterity == AbilityScore.SCORE_12 + 2

        constitution = character.abilities.get(
            ability_type=AbilityName.CONSTITUTION
        ).score
        assert constitution == AbilityScore.SCORE_13

        intelligence = character.abilities.get(
            ability_type=AbilityName.INTELLIGENCE
        ).score
        assert intelligence == AbilityScore.SCORE_14

        wisdom = character.abilities.get(ability_type=AbilityName.WISDOM).score
        assert wisdom == AbilityScore.SCORE_15

        charisma = character.abilities.get(ability_type=AbilityName.CHARISMA).score
        assert charisma == AbilityScore.SCORE_8

        assert character.speed == 25

        languages = set()
        languages.add(Language.objects.get(name=LanguageName.COMMON))
        languages.add(Language.objects.get(name=LanguageName.HALFLING))
        assert set(character.languages.all()) == languages

        senses = set()
        senses.add(Sense.objects.get(name=SenseName.LUCKY))
        senses.add(Sense.objects.get(name=SenseName.BRAVE))
        senses.add(Sense.objects.get(name=SenseName.HALFLING_NIMBLENESS))
        assert set(character.senses.all()) == senses

    @pytest.fixture
    def human_form(self):
        fake = Faker()
        return {
            "name": f"{fake.name()}",
            "race": f"{Race.HUMAN}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }

    def test_character_creation_human(self, client, human_form):
        form = CharacterCreateForm(human_form)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        assert 4.8 < character.height <= 4.8 + 2 * 10 / 12
        assert 110 < character.weight <= 110 + 2 * 4 * 12

        strength = character.abilities.get(ability_type=AbilityName.STRENGTH).score
        assert strength == AbilityScore.SCORE_10 + 1

        dexterity = character.abilities.get(ability_type=AbilityName.DEXTERITY).score
        assert dexterity == AbilityScore.SCORE_12 + 1

        constitution = character.abilities.get(
            ability_type=AbilityName.CONSTITUTION
        ).score
        assert constitution == AbilityScore.SCORE_13 + 1

        intelligence = character.abilities.get(
            ability_type=AbilityName.INTELLIGENCE
        ).score
        assert intelligence == AbilityScore.SCORE_14 + 1

        wisdom = character.abilities.get(ability_type=AbilityName.WISDOM).score
        assert wisdom == AbilityScore.SCORE_15 + 1

        charisma = character.abilities.get(ability_type=AbilityName.CHARISMA).score
        assert charisma == AbilityScore.SCORE_8 + 1

        assert character.speed == 30

        languages = set()
        languages.add(Language.objects.get(name=LanguageName.COMMON))
        assert set(character.languages.all()) == languages

        senses = set()
        assert set(character.senses.all()) == senses

    def test_character_creation_cleric(self, client):
        fake = Faker()
        name = fake.name()
        race = fake.enum(enum_cls=Race)
        klass = Klass.CLERIC
        gender = fake.enum(enum_cls=Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "klass": f"{klass}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{gender}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        assert character.hit_dice == "1d8"

        constitution_modifier = character.abilities.get(
            ability_type=AbilityName.CONSTITUTION
        ).modifier
        hp = 100 + 8 + constitution_modifier
        assert character.hp == hp

        assert set(character.savingthrowproficiency_set.all()) == set(
            SavingThrowProficiency.objects.filter(
                Q(ability_type_id=AbilityName.WISDOM)
                | Q(ability_type_id=AbilityName.CHARISMA)
            )
        )

    def test_character_creation_fighter(self, client):
        fake = Faker()
        name = fake.name()
        race = fake.enum(enum_cls=Race)
        klass = Klass.FIGHTER
        gender = fake.enum(enum_cls=Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "klass": f"{klass}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{gender}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

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

    def test_character_creation_rogue(self, client):
        fake = Faker()
        name = fake.name()
        race = fake.enum(enum_cls=Race)
        klass = Klass.ROGUE
        gender = fake.enum(enum_cls=Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "klass": f"{klass}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{gender}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

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

    def test_character_creation_wizard(self, client):
        fake = Faker()
        name = fake.name()
        race = fake.enum(enum_cls=Race)
        klass = Klass.WIZARD
        gender = fake.enum(enum_cls=Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "klass": f"{klass}",
            "background": f"{fake.enum(enum_cls=Background)}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{gender}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

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

    def test_character_creation_acolyte(self, client):
        fake = Faker()
        data = {
            "name": f"{fake.name()}",
            "race": f"{fake.enum(enum_cls=Race)}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{Background.ACOLYTE}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

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

    def test_character_creation_criminal(self, client):
        fake = Faker()
        data = {
            "name": f"{fake.name()}",
            "race": f"{fake.enum(enum_cls=Race)}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{Background.CRIMINAL}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        SkillProficiency.objects.filter(
            Q(character=character, skill=Skill.objects.get(name=SkillName.DECEPTION))
            | Q(character=character, skill=Skill.objects.get(name=SkillName.STEALTH))
        )

        assert (
            character.personality_trait
            in BACKGROUNDS[Background.CRIMINAL]["personality_traits"].values()
        )
        assert character.ideal in BACKGROUNDS[Background.CRIMINAL]["ideals"].values()
        assert character.bond in BACKGROUNDS[Background.CRIMINAL]["bonds"].values()
        assert character.flaw in BACKGROUNDS[Background.CRIMINAL]["flaws"].values()

    def test_character_creation_folk_hero(self, client):
        fake = Faker()
        data = {
            "name": f"{fake.name()}",
            "race": f"{fake.enum(enum_cls=Race)}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{Background.FOLK_HERO}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        SkillProficiency.objects.filter(
            Q(
                character=character,
                skill=Skill.objects.get(name=SkillName.ANIMAL_HANDLING),
            )
            | Q(character=character, skill=Skill.objects.get(name=SkillName.SURVIVAL))
        )

        assert (
            character.personality_trait
            in BACKGROUNDS[Background.FOLK_HERO]["personality_traits"].values()
        )
        assert character.ideal in BACKGROUNDS[Background.FOLK_HERO]["ideals"].values()
        assert character.bond in BACKGROUNDS[Background.FOLK_HERO]["bonds"].values()
        assert character.flaw in BACKGROUNDS[Background.FOLK_HERO]["flaws"].values()

    def test_character_creation_noble(self, client):
        fake = Faker()
        data = {
            "name": f"{fake.name()}",
            "race": f"{fake.enum(enum_cls=Race)}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{Background.NOBLE}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        SkillProficiency.objects.filter(
            Q(character=character, skill=Skill.objects.get(name=SkillName.HISTORY))
            | Q(character=character, skill=Skill.objects.get(name=SkillName.PERSUASION))
        )

        assert (
            character.personality_trait
            in BACKGROUNDS[Background.NOBLE]["personality_traits"].values()
        )
        assert character.ideal in BACKGROUNDS[Background.NOBLE]["ideals"].values()
        assert character.bond in BACKGROUNDS[Background.NOBLE]["bonds"].values()
        assert character.flaw in BACKGROUNDS[Background.NOBLE]["flaws"].values()

    def test_character_creation_sage(self, client):
        fake = Faker()
        data = {
            "name": f"{fake.name()}",
            "race": f"{fake.enum(enum_cls=Race)}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{Background.SAGE}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

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

    def test_character_creation_soldier(self, client):
        fake = Faker()
        data = {
            "name": f"{fake.name()}",
            "race": f"{fake.enum(enum_cls=Race)}",
            "klass": f"{fake.enum(enum_cls=Klass)}",
            "background": f"{Background.SOLDIER}",
            "strength": AbilityScore.SCORE_10,
            "dexterity": AbilityScore.SCORE_12,
            "constitution": AbilityScore.SCORE_13,
            "intelligence": AbilityScore.SCORE_14,
            "wisdom": AbilityScore.SCORE_15,
            "charisma": AbilityScore.SCORE_8,
            "gender": f"{fake.enum(enum_cls=Gender)}",
        }
        form = CharacterCreateForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

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
