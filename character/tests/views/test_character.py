import pytest
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from character.forms.character import CharacterCreateForm
from character.models.character import AbilityType, Character
from character.models.classes import Class
from character.models.races import Language, Race, Sense
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
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.character = CharacterFactory(name="character")
        client.force_login(self.character.user)

    def test_view_mapping(self, client):
        response = client.get(self.character.get_absolute_url())
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterDetailView

    def test_template_mapping(self, client):
        response = client.get(self.character.get_absolute_url())
        assert response.status_code == 200
        assertTemplateUsed(response, "character/character.html")

    def test_content_character_is_in_game(self, client):
        game = GameFactory()
        PlayerFactory(game=game, character=self.character)
        response = client.get(self.character.get_absolute_url())
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

    @pytest.fixture()
    def setup(self, client):
        user = UserFactory(username="user")
        client.force_login(user)

    def test_view_mapping(self, client, character):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterListView

    def test_template_mapping(self, client, setup):
        response = client.get(reverse(self.path_name))
        assertTemplateUsed(response, "character/character_list.html")

    def test_pagination_size(self, client, setup, create_characters):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 20

    def test_pagination_size_next_page(self, client, setup, create_characters):
        response = client.get(reverse(self.path_name) + "?page=2")
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 2

    def test_ordering(self, client, setup, create_characters):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        xp = 0
        for character in response.context["character_list"]:
            if xp == 0:
                xp = character.xp
            else:
                assert xp >= character.xp
                xp = character.xp

    @pytest.fixture
    def delete_characters(self):
        Character.objects.all().delete()

    def test_content_no_existing_character(self, client, setup, delete_characters):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertContains(response, "There is no character available...")

    def test_content_character_is_in_game(self, client, setup, delete_characters):
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
    def setup(self, client):
        user = UserFactory(username="user")
        client.force_login(user)

    def test_view_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class, CharacterCreateView

    def test_template_mapping(self, client):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assertTemplateUsed(response, "character/character_create.html")

    def test_character_creation_common(self, client):
        fake = Faker()
        name = fake.name()
        race = fake.enum(enum_cls=Race)
        class_name = fake.enum(enum_cls=Class)
        gender = fake.enum(enum_cls=Character.Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "class_name": f"{class_name}",
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

        assert character.name, form.cleaned_data["name"]
        assert character.race, form.cleaned_data["race"]
        assert character.xp == 0
        assert character.hp >= 100
        assert character.max_hp >= 100
        assert character.hp == character.max_hp

    def test_character_creation_dwarf(self, client):
        fake = Faker()
        name = fake.name()
        race = Race.DWARF
        class_name = fake.enum(enum_cls=Class)
        gender = fake.enum(enum_cls=Character.Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "class_name": f"{class_name}",
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

        strength = character.abilities.get(ability_type=AbilityType.Name.STRENGTH).score
        assert strength == AbilityScore.SCORE_10

        dexterity = character.abilities.get(
            ability_type=AbilityType.Name.DEXTERITY
        ).score
        assert dexterity == AbilityScore.SCORE_12

        constitution = character.abilities.get(
            ability_type=AbilityType.Name.CONSTITUTION
        ).score
        assert constitution == AbilityScore.SCORE_13 + 2

        intelligence = character.abilities.get(
            ability_type=AbilityType.Name.INTELLIGENCE
        ).score
        assert intelligence == AbilityScore.SCORE_14

        wisdom = character.abilities.get(ability_type=AbilityType.Name.WISDOM).score
        assert wisdom == AbilityScore.SCORE_15

        charisma = character.abilities.get(ability_type=AbilityType.Name.CHARISMA).score
        assert charisma == AbilityScore.SCORE_8

        assert character.speed == 25

        common = Language.objects.get(name=Language.Name.COMMON)
        dwarvish = Language.objects.get(name=Language.Name.DWARVISH)
        languages = set()
        languages.add(common)
        languages.add(dwarvish)
        assert set(character.languages.all()) == languages

        darkvision = Sense.objects.get(name="Darkvision")
        dwarven_resilience = Sense.objects.get(name="Dwarven Resilience")
        dwarven_combat_training = Sense.objects.get(name="Dwarven Combat Training")
        tool_proficiency = Sense.objects.get(name="Tool Proficiency")
        stonecunning = Sense.objects.get(name="Stonecunning")
        senses = set()
        senses.add(darkvision)
        senses.add(dwarven_resilience)
        senses.add(dwarven_combat_training)
        senses.add(tool_proficiency)
        senses.add(stonecunning)
        assert set(character.senses.all()) == senses

    def test_character_creation_elf(self, client):
        fake = Faker()
        name = fake.name()
        race = Race.ELF
        class_name = fake.enum(enum_cls=Class)
        gender = fake.enum(enum_cls=Character.Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "class_name": f"{class_name}",
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
        assert response.status_code, 302
        character = Character.objects.last()
        assertRedirects(response, reverse("skills-select", args=(character.id,)))

        strength = character.abilities.get(ability_type=AbilityType.Name.STRENGTH).score
        assert strength == AbilityScore.SCORE_10

        dexterity = character.abilities.get(
            ability_type=AbilityType.Name.DEXTERITY
        ).score
        assert dexterity == AbilityScore.SCORE_12 + 2

        constitution = character.abilities.get(
            ability_type=AbilityType.Name.CONSTITUTION
        ).score
        assert constitution == AbilityScore.SCORE_13

        intelligence = character.abilities.get(
            ability_type=AbilityType.Name.INTELLIGENCE
        ).score
        assert intelligence == AbilityScore.SCORE_14

        wisdom = character.abilities.get(ability_type=AbilityType.Name.WISDOM).score
        assert wisdom == AbilityScore.SCORE_15

        charisma = character.abilities.get(ability_type=AbilityType.Name.CHARISMA).score
        assert charisma == AbilityScore.SCORE_8

        assert character.speed == 30

        elvish = Language.objects.get(name=Language.Name.ELVISH)
        languages = set()
        languages.add(elvish)
        assert set(character.languages.all()) == languages

        darkvision = Sense.objects.get(name="Darkvision")
        keen_senses = Sense.objects.get(name="Keen Senses")
        fey_ancestry = Sense.objects.get(name="Fey Ancestry")
        trance = Sense.objects.get(name="Trance")
        senses = set()
        senses.add(darkvision)
        senses.add(keen_senses)
        senses.add(fey_ancestry)
        senses.add(trance)
        assert set(character.senses.all()) == senses

    def test_character_creation_halfling(self, client):
        fake = Faker()
        name = fake.name()
        race = Race.HALFLING
        class_name = fake.enum(enum_cls=Class)
        gender = fake.enum(enum_cls=Character.Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "class_name": f"{class_name}",
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

        strength = character.abilities.get(ability_type=AbilityType.Name.STRENGTH).score
        assert strength == AbilityScore.SCORE_10

        dexterity = character.abilities.get(
            ability_type=AbilityType.Name.DEXTERITY
        ).score
        assert dexterity == AbilityScore.SCORE_12 + 2

        constitution = character.abilities.get(
            ability_type=AbilityType.Name.CONSTITUTION
        ).score
        assert constitution == AbilityScore.SCORE_13

        intelligence = character.abilities.get(
            ability_type=AbilityType.Name.INTELLIGENCE
        ).score
        assert intelligence == AbilityScore.SCORE_14

        wisdom = character.abilities.get(ability_type=AbilityType.Name.WISDOM).score
        assert wisdom == AbilityScore.SCORE_15

        charisma = character.abilities.get(ability_type=AbilityType.Name.CHARISMA).score
        assert charisma == AbilityScore.SCORE_8

        assert character.speed == 25

        common = Language.objects.get(name=Language.Name.COMMON)
        halfling = Language.objects.get(name=Language.Name.HALFLING)
        languages = set()
        languages.add(common)
        languages.add(halfling)
        assert set(character.languages.all()) == languages

        lucky = Sense.objects.get(name="Lucky")
        brave = Sense.objects.get(name="Brave")
        halfling_nimbleness = Sense.objects.get(name="Halfling Nimbleness")
        senses = set()
        senses.add(lucky)
        senses.add(brave)
        senses.add(halfling_nimbleness)
        assert set(character.senses.all()) == senses

    def test_character_creation_human(self, client):
        fake = Faker()
        name = fake.name()
        race = Race.HUMAN
        class_name = fake.enum(enum_cls=Class)
        gender = fake.enum(enum_cls=Character.Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "class_name": f"{class_name}",
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

        strength = character.abilities.get(ability_type=AbilityType.Name.STRENGTH).score
        assert strength == AbilityScore.SCORE_10 + 1

        dexterity = character.abilities.get(
            ability_type=AbilityType.Name.DEXTERITY
        ).score
        assert dexterity == AbilityScore.SCORE_12 + 1

        constitution = character.abilities.get(
            ability_type=AbilityType.Name.CONSTITUTION
        ).score
        assert constitution == AbilityScore.SCORE_13 + 1

        intelligence = character.abilities.get(
            ability_type=AbilityType.Name.INTELLIGENCE
        ).score
        assert intelligence == AbilityScore.SCORE_14 + 1

        wisdom = character.abilities.get(ability_type=AbilityType.Name.WISDOM).score
        assert wisdom == AbilityScore.SCORE_15 + 1

        charisma = character.abilities.get(ability_type=AbilityType.Name.CHARISMA).score
        assert charisma == AbilityScore.SCORE_8 + 1

        assert character.speed == 30

        common = Language.objects.get(name=Language.Name.COMMON)
        languages = set()
        languages.add(common)
        assert set(character.languages.all()) == languages

        senses = set()
        assert set(character.senses.all()) == senses

    def test_character_creation_cleric(self, client):
        fake = Faker()
        name = fake.name()
        race = fake.enum(enum_cls=Race)
        class_name = Class.CLERIC
        gender = fake.enum(enum_cls=Character.Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "class_name": f"{class_name}",
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
            ability_type=AbilityType.Name.CONSTITUTION
        ).modifier
        hp = 100 + 8 + constitution_modifier
        assert character.hp == hp

        assert character.proficiencies.armor == "Light armor, medium armor, shields"

        assert character.proficiencies.weapons == "Simple weapons"
        assert character.proficiencies.tools == "None"
        assert character.proficiencies.saving_throws == "Wisdom, Charisma"

    def test_character_creation_fighter(self, client):
        fake = Faker()
        name = fake.name()
        race = fake.enum(enum_cls=Race)
        class_name = Class.FIGHTER
        gender = fake.enum(enum_cls=Character.Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "class_name": f"{class_name}",
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
            ability_type=AbilityType.Name.CONSTITUTION
        ).modifier
        hp = 100 + 10 + constitution_modifier
        assert character.hp == hp

        assert character.proficiencies.armor == "All armor, shields"
        assert character.proficiencies.weapons == "Simple weapons, martial weapons"
        assert character.proficiencies.tools == "None"
        assert character.proficiencies.saving_throws == "Strength, Constitution"

    def test_character_creation_rogue(self, client):
        fake = Faker()
        name = fake.name()
        race = fake.enum(enum_cls=Race)
        class_name = Class.ROGUE
        gender = fake.enum(enum_cls=Character.Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "class_name": f"{class_name}",
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
            ability_type=AbilityType.Name.CONSTITUTION
        ).modifier
        hp = 100 + 8 + constitution_modifier
        assert character.hp == hp

        assert character.proficiencies.armor == "Light armor"
        assert (
            character.proficiencies.weapons
            == "Simple weapons, hand crossbows, longswords, rapiers, shortswords"
        )
        assert character.proficiencies.tools == "Thieves' tools"
        assert character.proficiencies.saving_throws == "Dexterity, Intelligence"

    def test_character_creation_wizard(self, client):
        fake = Faker()
        name = fake.name()
        race = fake.enum(enum_cls=Race)
        class_name = Class.WIZARD
        gender = fake.enum(enum_cls=Character.Gender)
        data = {
            "name": f"{name}",
            "race": f"{race}",
            "class_name": f"{class_name}",
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
            ability_type=AbilityType.Name.CONSTITUTION
        ).modifier
        hp = 100 + 6 + constitution_modifier
        assert character.hp == hp

        assert character.proficiencies.armor == "None"
        assert (
            character.proficiencies.weapons
            == "Daggers, darts, slings, quarterstaffs, light crossbows"
        )
        assert character.proficiencies.tools == "None"
        assert character.proficiencies.saving_throws == "Intelligence, Wisdom"
