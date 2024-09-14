import pytest
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from character.constants.klasses import Klass
from character.constants.skills import SkillName
from character.forms.skills import ExtendedSkillsSelectForm, SkillsSelectForm
from character.views.skills import SkillsSelectView
from utils.converters import duplicate_choice


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
        skills_set = {
            duplicate_choice(SkillName.HISTORY),
            duplicate_choice(SkillName.INSIGHT),
            duplicate_choice(SkillName.MEDICINE),
            duplicate_choice(SkillName.PERSUASION),
            duplicate_choice(SkillName.RELIGION),
        }
        skills = fake.random_elements(
            elements=sorted(skills_set), length=len(skills_set), unique=True
        )
        data = {
            "first_skill": f"{skills[0][0]}",
            "second_skill": f"{skills[1][0]}",
        }
        form = SkillsSelectForm(initial={"klass": Klass.CLERIC}, data=data)
        assert form.is_valid()

        character = cleric  # for better readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("background-complete", args=(character.id,)))

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
        skills_set = {
            duplicate_choice(SkillName.ACROBATICS),
            duplicate_choice(SkillName.ANIMAL_HANDLING),
            duplicate_choice(SkillName.ATHLETICS),
            duplicate_choice(SkillName.HISTORY),
            duplicate_choice(SkillName.INSIGHT),
            duplicate_choice(SkillName.INTIMIDATION),
            duplicate_choice(SkillName.PERCEPTION),
            duplicate_choice(SkillName.SURVIVAL),
        }
        skills = fake.random_elements(
            elements=sorted(skills_set), length=len(skills_set), unique=True
        )
        data = {
            "first_skill": f"{skills[0][0]}",
            "second_skill": f"{skills[1][0]}",
        }
        form = SkillsSelectForm(initial={"klass": Klass.FIGHTER}, data=data)
        assert form.is_valid()

        character = fighter  # for better readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("background-complete", args=(character.id,)))

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
        skills_set = {
            duplicate_choice(SkillName.ACROBATICS),
            duplicate_choice(SkillName.ATHLETICS),
            duplicate_choice(SkillName.DECEPTION),
            duplicate_choice(SkillName.INSIGHT),
            duplicate_choice(SkillName.INTIMIDATION),
            duplicate_choice(SkillName.INVESTIGATION),
            duplicate_choice(SkillName.PERCEPTION),
            duplicate_choice(SkillName.PERFORMANCE),
            duplicate_choice(SkillName.PERSUASION),
            duplicate_choice(SkillName.SLEIGHT_OF_HAND),
            duplicate_choice(SkillName.STEALTH),
        }
        skills = fake.random_elements(
            elements=sorted(skills_set), length=len(skills_set), unique=True
        )
        data = {
            "first_skill": f"{skills[0][0]}",
            "second_skill": f"{skills[1][0]}",
            "third_skill": f"{skills[2][0]}",
            "fourth_skill": f"{skills[3][0]}",
        }
        form = ExtendedSkillsSelectForm(initial={"klass": Klass.ROGUE}, data=data)
        assert form.is_valid()

        character = rogue  # for better readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("background-complete", args=(character.id,)))

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
        skills_set = {
            duplicate_choice(SkillName.ARCANA),
            duplicate_choice(SkillName.HISTORY),
            duplicate_choice(SkillName.INSIGHT),
            duplicate_choice(SkillName.INVESTIGATION),
            duplicate_choice(SkillName.MEDICINE),
            duplicate_choice(SkillName.RELIGION),
        }
        skills = fake.random_elements(
            elements=sorted(skills_set), length=len(skills_set), unique=True
        )
        data = {
            "first_skill": f"{skills[0][0]}",
            "second_skill": f"{skills[1][0]}",
        }
        form = SkillsSelectForm(initial={"klass": Klass.WIZARD}, data=data)
        assert form.is_valid()

        character = wizard  # for better readability
        response = client.post(
            reverse(self.path_name, args=(character.id,)),
            data=form.cleaned_data,
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("background-complete", args=(character.id,)))

        assert any(
            skills[0][0] in skill
            for skill in list(character.skills.all().values_list())
        )
        assert any(
            skills[1][0] in skill
            for skill in list(character.skills.all().values_list())
        )
