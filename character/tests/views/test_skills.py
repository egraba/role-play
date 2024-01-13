import pytest
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from character.forms.skills import ExtendedSkillsSelectForm, SkillsSelectForm
from character.utils.skills import (
    cleric_choices,
    fighter_choices,
    rogue_choices,
    wizard_choices,
)
from character.views.skills import SkillsSelectView


@pytest.mark.django_db
class TestSkillsSelectView:
    path_name = "skills-select"
    character = None

    def test_view_mapping(self, client, character):
        response = client.get(reverse(self.path_name, args=(character.id,)))
        assert response.status_code == 200
        assert response.resolver_match.func.view_class == SkillsSelectView

    def test_template_mapping(self, client, character):
        response = client.get(reverse(self.path_name, args=(character.id,)))
        assert response.status_code == 200
        assertTemplateUsed(response, "character/skills_select.html")

    def test_cleric_skills(self, client, cleric):
        fake = Faker()
        skills = fake.random_elements(
            elements=sorted(cleric_choices), length=len(cleric_choices), unique=True
        )
        data = {
            "first_skill": f"{skills[0][0]}",
            "second_skill": f"{skills[1][0]}",
        }
        form = SkillsSelectForm(initial={"choices": cleric_choices}, data=data)
        assert form.is_valid()

        character = cleric  # for better readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert any(
            skills[0][0] in skill
            for skill in list(character.skills.all().values_list())
        )
        assert any(
            skills[1][0] in skill
            for skill in list(character.skills.all().values_list())
        )

    def test_fighter_skills(self, client, fighter):
        fake = Faker()
        skills = fake.random_elements(
            elements=sorted(fighter_choices), length=len(fighter_choices), unique=True
        )
        data = {
            "first_skill": f"{skills[0][0]}",
            "second_skill": f"{skills[1][0]}",
        }
        form = SkillsSelectForm(initial={"choices": fighter_choices}, data=data)
        assert form.is_valid()

        character = fighter  # for better readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert any(
            skills[0][0] in skill
            for skill in list(character.skills.all().values_list())
        )
        assert any(
            skills[1][0] in skill
            for skill in list(character.skills.all().values_list())
        )

    def test_rogue_skills(self, client, rogue):
        fake = Faker()
        skills = fake.random_elements(
            elements=sorted(rogue_choices), length=len(rogue_choices), unique=True
        )
        data = {
            "first_skill": f"{skills[0][0]}",
            "second_skill": f"{skills[1][0]}",
            "third_skill": f"{skills[2][0]}",
            "fourth_skill": f"{skills[3][0]}",
        }
        form = ExtendedSkillsSelectForm(initial={"choices": rogue_choices}, data=data)
        assert form.is_valid()

        character = rogue  # for better readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert any(
            skills[0][0] in skill
            for skill in list(character.skills.all().values_list())
        )
        assert any(
            skills[1][0] in skill
            for skill in list(character.skills.all().values_list())
        )
        assert any(
            skills[2][0] in skill
            for skill in list(character.skills.all().values_list())
        )
        assert any(
            skills[3][0] in skill
            for skill in list(character.skills.all().values_list())
        )

    def test_wizard_skills(self, client, wizard):
        fake = Faker()
        skills = fake.random_elements(
            elements=sorted(wizard_choices), length=len(wizard_choices), unique=True
        )
        data = {
            "first_skill": f"{skills[0][0]}",
            "second_skill": f"{skills[1][0]}",
        }
        form = SkillsSelectForm(initial={"choices": wizard_choices}, data=data)
        assert form.is_valid()

        character = wizard  # for better readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("equipment-select", args=(character.id,)))

        assert any(
            skills[0][0] in skill
            for skill in list(character.skills.all().values_list())
        )
        assert any(
            skills[1][0] in skill
            for skill in list(character.skills.all().values_list())
        )
