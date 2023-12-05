import pytest
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from character.forms.character import CreateCharacterForm
from character.models.character import Character
from character.models.classes import Class
from character.models.races import Ability, Language, Race
from character.utils.abilities import AbilityScore
from character.views.character import (
    CharacterCreateView,
    CharacterDetailView,
    CharacterListView,
)
from utils.testing.factories import (
    CharacterFactory,
    GameFactory,
    PlayerFactory,
    UserFactory,
)


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


@pytest.mark.django_db
class TestCharacterListView:
    path_name = "character-list"

    @pytest.fixture()
    def setup(self, client):
        user = UserFactory(username="user")
        client.force_login(user)

    def test_view_mapping(self, client, setup):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == CharacterListView

    def test_template_mapping(self, client, setup):
        response = client.get(reverse(self.path_name))
        assertTemplateUsed(response, "character/character_list.html")

    def test_pagination_size(self, client, setup, setup_characters):
        response = client.get(reverse(self.path_name))
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 20

    def test_pagination_size_next_page(self, client, setup, setup_characters):
        response = client.get(reverse(self.path_name) + "?page=2")
        assert response.status_code == 200
        assert "is_paginated" in response.context
        assert response.context["is_paginated"]
        assert len(response.context["character_list"]) == 2

    def test_ordering(self, client, setup, setup_characters):
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
    fixtures = ["races", "abilities", "classes", "equipment"]

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

    def test_character_creation_common(self, client, character_fixtures):
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
        form = CreateCharacterForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

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
        form = CreateCharacterForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert character.strength == AbilityScore.SCORE_10
        assert character.dexterity == AbilityScore.SCORE_12
        assert character.constitution == AbilityScore.SCORE_13 + 2
        assert character.intelligence == AbilityScore.SCORE_14
        assert character.wisdom == AbilityScore.SCORE_15
        assert character.charisma == AbilityScore.SCORE_8

        assert character.speed == 25

        common = Language.objects.get(name=Language.Name.COMMON)
        dwarvish = Language.objects.get(name=Language.Name.DWARVISH)
        languages = set()
        languages.add(common)
        languages.add(dwarvish)
        assert set(character.languages.all()) == languages

        darkvision = Ability.objects.get(name="Darkvision")
        dwarven_resilience = Ability.objects.get(name="Dwarven Resilience")
        dwarven_combat_training = Ability.objects.get(name="Dwarven Combat Training")
        tool_proficiency = Ability.objects.get(name="Tool Proficiency")
        stonecunning = Ability.objects.get(name="Stonecunning")
        abilities = set()
        abilities.add(darkvision)
        abilities.add(dwarven_resilience)
        abilities.add(dwarven_combat_training)
        abilities.add(tool_proficiency)
        abilities.add(stonecunning)
        assert set(character.abilities.all()) == abilities

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
        form = CreateCharacterForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code, 302
        character = Character.objects.last()
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert character.strength == AbilityScore.SCORE_10
        assert character.dexterity == AbilityScore.SCORE_12 + 2
        assert character.constitution == AbilityScore.SCORE_13
        assert character.intelligence == AbilityScore.SCORE_14
        assert character.wisdom == AbilityScore.SCORE_15
        assert character.charisma == AbilityScore.SCORE_8

        assert character.speed == 30

        elvish = Language.objects.get(name=Language.Name.ELVISH)
        languages = set()
        languages.add(elvish)
        assert set(character.languages.all()) == languages

        darkvision = Ability.objects.get(name="Darkvision")
        keen_senses = Ability.objects.get(name="Keen Senses")
        fey_ancestry = Ability.objects.get(name="Fey Ancestry")
        trance = Ability.objects.get(name="Trance")
        abilities = set()
        abilities.add(darkvision)
        abilities.add(keen_senses)
        abilities.add(fey_ancestry)
        abilities.add(trance)
        assert set(character.abilities.all()) == abilities

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
        form = CreateCharacterForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert character.strength == AbilityScore.SCORE_10
        assert character.dexterity == AbilityScore.SCORE_12 + 2
        assert character.constitution == AbilityScore.SCORE_13
        assert character.intelligence == AbilityScore.SCORE_14
        assert character.wisdom == AbilityScore.SCORE_15
        assert character.charisma, AbilityScore.SCORE_8

        assert character.speed == 25

        common = Language.objects.get(name=Language.Name.COMMON)
        halfling = Language.objects.get(name=Language.Name.HALFLING)
        languages = set()
        languages.add(common)
        languages.add(halfling)
        assert set(character.languages.all()) == languages

        lucky = Ability.objects.get(name="Lucky")
        brave = Ability.objects.get(name="Brave")
        halfling_nimbleness = Ability.objects.get(name="Halfling Nimbleness")
        abilities = set()
        abilities.add(lucky)
        abilities.add(brave)
        abilities.add(halfling_nimbleness)
        assert set(character.abilities.all()) == abilities

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
        form = CreateCharacterForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert character.strength == AbilityScore.SCORE_10 + 1
        assert character.dexterity == AbilityScore.SCORE_12 + 1
        assert character.constitution == AbilityScore.SCORE_13 + 1
        assert character.intelligence == AbilityScore.SCORE_14 + 1
        assert character.wisdom == AbilityScore.SCORE_15 + 1
        assert character.charisma == AbilityScore.SCORE_8 + 1

        assert character.speed == 30

        common = Language.objects.get(name=Language.Name.COMMON)
        languages = set()
        languages.add(common)
        assert set(character.languages.all()) == languages

        abilities = set()
        assert set(character.abilities.all()) == abilities

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
        form = CreateCharacterForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert character.hit_dice == "1d8"

        hp = 100 + 8 + character.constitution_modifier
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
        form = CreateCharacterForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert character.hit_dice == "1d10"

        hp = 100 + 10 + character.constitution_modifier
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
        form = CreateCharacterForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert character.hit_dice == "1d8"

        hp = 100 + 8 + character.constitution_modifier
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
        form = CreateCharacterForm(data)
        assert form.is_valid()

        response = client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        character = Character.objects.last()
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert character.hit_dice == "1d6"

        hp = 100 + 6 + character.constitution_modifier
        assert character.hp == hp

        assert character.proficiencies.armor == "None"
        assert (
            character.proficiencies.weapons
            == "Daggers, darts, slings, quarterstaffs, light crossbows"
        )
        assert character.proficiencies.tools == "None"
        assert character.proficiencies.saving_throws == "Intelligence, Wisdom"
