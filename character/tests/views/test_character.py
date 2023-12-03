import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertContains, assertTemplateUsed

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


class CharacterDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        CharacterFactory()

    def setUp(self):
        self.user = User.objects.last()
        self.client.force_login(self.user)
        self.character = Character.objects.last()

    def test_view_mapping(self):
        response = self.client.get(self.character.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, CharacterDetailView)

    def test_template_mapping(self):
        response = self.client.get(self.character.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "character/character.html")

    def test_content_character_is_in_game(self):
        game = GameFactory()
        PlayerFactory(game=game, character=self.character)
        response = self.client.get(self.character.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, game.name)


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


class CharacterCreateViewTest(TestCase):
    path_name = "character-create"
    fixtures = ["races", "abilities", "classes", "equipment"]

    @classmethod
    def setUpTestData(cls):
        CharacterFactory()

    def setUp(self):
        self.user = User.objects.last()
        self.client.force_login(self.user)

    def test_view_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, CharacterCreateView)

    def test_template_mapping(self):
        response = self.client.get(reverse(self.path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "character/character_create.html")

    def test_character_creation_common(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("equipment-select", args=(character.id,))
        )

        self.assertEqual(character.name, form.cleaned_data["name"])
        self.assertEqual(character.race, form.cleaned_data["race"])
        self.assertEqual(character.xp, 0)
        self.assertGreaterEqual(character.hp, 100)
        self.assertGreaterEqual(character.max_hp, 100)
        self.assertEqual(character.hp, character.max_hp)

    def test_character_creation_dwarf(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("equipment-select", args=(character.id,))
        )

        self.assertEqual(character.strength, AbilityScore.SCORE_10)
        self.assertEqual(character.dexterity, AbilityScore.SCORE_12)
        self.assertEqual(character.constitution, AbilityScore.SCORE_13 + 2)
        self.assertEqual(character.intelligence, AbilityScore.SCORE_14)
        self.assertEqual(character.wisdom, AbilityScore.SCORE_15)
        self.assertEqual(character.charisma, AbilityScore.SCORE_8)

        self.assertEqual(character.speed, 25)

        common = Language.objects.get(name=Language.Name.COMMON)
        dwarvish = Language.objects.get(name=Language.Name.DWARVISH)
        languages = set()
        languages.add(common)
        languages.add(dwarvish)
        self.assertEqual(set(character.languages.all()), languages)

        darkvision = Ability.objects.get(name="Darkvision")
        dwarven_resilience = Ability.objects.get(name="Dwarven Resilience")
        dwarven_combat_training = Ability.objects.get(name="Dwarven Combat Training")
        tool_proficiency = Ability.objects.get(name="Tool Proficiency")
        stonecunning = Ability.objects.get(name="Stonecunning")
        abtls = set()
        abtls.add(darkvision)
        abtls.add(dwarven_resilience)
        abtls.add(dwarven_combat_training)
        abtls.add(tool_proficiency)
        abtls.add(stonecunning)
        self.assertEqual(set(character.abilities.all()), abtls)

    def test_character_creation_elf(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("equipment-select", args=(character.id,))
        )

        self.assertEqual(character.strength, AbilityScore.SCORE_10)
        self.assertEqual(character.dexterity, AbilityScore.SCORE_12 + 2)
        self.assertEqual(character.constitution, AbilityScore.SCORE_13)
        self.assertEqual(character.intelligence, AbilityScore.SCORE_14)
        self.assertEqual(character.wisdom, AbilityScore.SCORE_15)
        self.assertEqual(character.charisma, AbilityScore.SCORE_8)

        self.assertEqual(character.speed, 30)

        elvish = Language.objects.get(name=Language.Name.ELVISH)
        languages = set()
        languages.add(elvish)
        self.assertEqual(set(character.languages.all()), languages)

        darkvision = Ability.objects.get(name="Darkvision")
        keen_senses = Ability.objects.get(name="Keen Senses")
        fey_ancestry = Ability.objects.get(name="Fey Ancestry")
        trance = Ability.objects.get(name="Trance")
        abtls = set()
        abtls.add(darkvision)
        abtls.add(keen_senses)
        abtls.add(fey_ancestry)
        abtls.add(trance)
        self.assertEqual(set(character.abilities.all()), abtls)

    def test_character_creation_halfling(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("equipment-select", args=(character.id,))
        )

        self.assertEqual(character.strength, AbilityScore.SCORE_10)
        self.assertEqual(character.dexterity, AbilityScore.SCORE_12 + 2)
        self.assertEqual(character.constitution, AbilityScore.SCORE_13)
        self.assertEqual(character.intelligence, AbilityScore.SCORE_14)
        self.assertEqual(character.wisdom, AbilityScore.SCORE_15)
        self.assertEqual(character.charisma, AbilityScore.SCORE_8)

        self.assertEqual(character.speed, 25)

        common = Language.objects.get(name=Language.Name.COMMON)
        halfling = Language.objects.get(name=Language.Name.HALFLING)
        languages = set()
        languages.add(common)
        languages.add(halfling)
        self.assertEqual(set(character.languages.all()), languages)

        lucky = Ability.objects.get(name="Lucky")
        brave = Ability.objects.get(name="Brave")
        halfling_nimbleness = Ability.objects.get(name="Halfling Nimbleness")
        abtls = set()
        abtls.add(lucky)
        abtls.add(brave)
        abtls.add(halfling_nimbleness)
        self.assertEqual(set(character.abilities.all()), abtls)

    def test_character_creation_human(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("equipment-select", args=(character.id,))
        )

        self.assertEqual(character.strength, AbilityScore.SCORE_10 + 1)
        self.assertEqual(character.dexterity, AbilityScore.SCORE_12 + 1)
        self.assertEqual(character.constitution, AbilityScore.SCORE_13 + 1)
        self.assertEqual(character.intelligence, AbilityScore.SCORE_14 + 1)
        self.assertEqual(character.wisdom, AbilityScore.SCORE_15 + 1)
        self.assertEqual(character.charisma, AbilityScore.SCORE_8 + 1)

        self.assertEqual(character.speed, 30)

        common = Language.objects.get(name=Language.Name.COMMON)
        languages = set()
        languages.add(common)
        self.assertEqual(set(character.languages.all()), languages)

        abtls = set()
        self.assertEqual(set(character.abilities.all()), abtls)

    def test_character_creation_cleric(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("equipment-select", args=(character.id,))
        )

        self.assertEqual(character.hit_dice, "1d8")

        hp = 100 + 8 + character.constitution_modifier
        self.assertEqual(character.hp, hp)

        self.assertEqual(
            character.proficiencies.armor, "Light armor, medium armor, shields"
        )
        self.assertEqual(character.proficiencies.weapons, "Simple weapons")
        self.assertEqual(character.proficiencies.tools, "None")
        self.assertEqual(character.proficiencies.saving_throws, "Wisdom, Charisma")

    def test_character_creation_fighter(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("equipment-select", args=(character.id,))
        )

        self.assertEqual(character.hit_dice, "1d10")

        hp = 100 + 10 + character.constitution_modifier
        self.assertEqual(character.hp, hp)

        self.assertEqual(character.proficiencies.armor, "All armor, shields")
        self.assertEqual(
            character.proficiencies.weapons,
            "Simple weapons, martial weapons",
        )
        self.assertEqual(character.proficiencies.tools, "None")
        self.assertEqual(
            character.proficiencies.saving_throws, "Strength, Constitution"
        )

    def test_character_creation_rogue(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("equipment-select", args=(character.id,))
        )

        self.assertEqual(character.hit_dice, "1d8")

        hp = 100 + 8 + character.constitution_modifier
        self.assertEqual(character.hp, hp)

        self.assertEqual(character.proficiencies.armor, "Light armor")
        self.assertEqual(
            character.proficiencies.weapons,
            "Simple weapons, hand crossbows, longswords, rapiers, shortswords",
        )
        self.assertEqual(character.proficiencies.tools, "Thieves' tools")
        self.assertEqual(
            character.proficiencies.saving_throws, "Dexterity, Intelligence"
        )

    def test_character_creation_wizard(self):
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
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse(self.path_name),
            data=form.cleaned_data,
        )
        self.assertEqual(response.status_code, 302)
        character = Character.objects.last()
        self.assertRedirects(
            response, reverse("equipment-select", args=(character.id,))
        )

        self.assertEqual(character.hit_dice, "1d6")

        hp = 100 + 6 + character.constitution_modifier
        self.assertEqual(character.hp, hp)

        self.assertEqual(character.proficiencies.armor, "None")
        self.assertEqual(
            character.proficiencies.weapons,
            "Daggers, darts, slings, quarterstaffs, light crossbows",
        )
        self.assertEqual(character.proficiencies.tools, "None")
        self.assertEqual(character.proficiencies.saving_throws, "Intelligence, Wisdom")
