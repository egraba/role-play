"""Tests for character creation wizard forms."""

import pytest
from django import forms

from character.constants.backgrounds import Background
from character.constants.classes import ClassName
from character.constants.skills import SkillName
from character.forms.wizard_forms import (
    AbilityScoreForm,
    BackgroundSelectForm,
    ClassSelectForm,
    EquipmentSelectForm,
    ReviewForm,
    SkillsSelectForm,
    SpeciesSelectForm,
    _get_num_skills,
    _get_skills,
)

from ..factories import CharacterFactory, ClassFactory, SpeciesFactory


pytestmark = pytest.mark.django_db


class TestSpeciesSelectForm:
    def test_form_has_species_field(self):
        form = SpeciesSelectForm()
        assert "species" in form.fields
        assert isinstance(form.fields["species"], forms.ModelChoiceField)

    def test_species_field_has_dropdown_class(self):
        form = SpeciesSelectForm()
        assert form.fields["species"].widget.attrs.get("class") == "rpgui-dropdown"

    def test_valid_form_with_species(self):
        species = SpeciesFactory()
        form = SpeciesSelectForm(data={"species": species.pk})
        assert form.is_valid(), form.errors

    def test_invalid_without_species(self):
        form = SpeciesSelectForm(data={})
        assert not form.is_valid()
        assert "species" in form.errors

    def test_get_species_preview_data_returns_dict(self):
        SpeciesFactory()
        form = SpeciesSelectForm()
        preview_data = form.get_species_preview_data()
        assert isinstance(preview_data, dict)

    def test_get_species_preview_data_contains_species_info(self):
        species = SpeciesFactory(speed=30)
        form = SpeciesSelectForm()
        preview_data = form.get_species_preview_data()
        assert species.name in preview_data
        assert preview_data[species.name]["speed"] == species.speed
        assert "darkvision" in preview_data[species.name]


class TestClassSelectForm:
    def test_form_has_klass_field(self):
        form = ClassSelectForm()
        assert "klass" in form.fields
        assert isinstance(form.fields["klass"], forms.ModelChoiceField)

    def test_klass_field_has_dropdown_class(self):
        form = ClassSelectForm()
        assert form.fields["klass"].widget.attrs.get("class") == "rpgui-dropdown"

    def test_valid_form_with_class(self):
        klass = ClassFactory()
        form = ClassSelectForm(data={"klass": klass.pk})
        assert form.is_valid(), form.errors

    def test_invalid_without_class(self):
        form = ClassSelectForm(data={})
        assert not form.is_valid()
        assert "klass" in form.errors

    def test_get_class_preview_data_returns_dict(self):
        ClassFactory()
        form = ClassSelectForm()
        preview_data = form.get_class_preview_data()
        assert isinstance(preview_data, dict)

    def test_get_class_preview_data_contains_class_info(self):
        klass = ClassFactory()
        form = ClassSelectForm()
        preview_data = form.get_class_preview_data()
        assert klass.name in preview_data
        assert preview_data[klass.name]["hit_die"] == f"d{klass.hit_die}"
        assert preview_data[klass.name]["hp_first_level"] == klass.hp_first_level


class TestAbilityScoreForm:
    @pytest.fixture
    def standard_array_data(self):
        return {
            "generation_method": "standard",
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
        }

    def test_form_has_all_ability_fields(self):
        form = AbilityScoreForm()
        assert "generation_method" in form.fields
        assert "strength" in form.fields
        assert "dexterity" in form.fields
        assert "constitution" in form.fields
        assert "intelligence" in form.fields
        assert "wisdom" in form.fields
        assert "charisma" in form.fields

    def test_valid_standard_array_form(self, standard_array_data):
        form = AbilityScoreForm(data=standard_array_data)
        assert form.is_valid(), form.errors

    def test_duplicate_ability_scores_rejected(self, standard_array_data):
        """Standard array requires unique values for each ability."""
        standard_array_data["dexterity"] = 15  # Duplicate of strength
        form = AbilityScoreForm(data=standard_array_data)
        assert not form.is_valid()

    def test_point_buy_validation_within_limit(self):
        """Point buy with valid total (27 points or less) and unique values."""
        data = {
            "generation_method": "point_buy",
            "strength": 15,  # 9 points
            "dexterity": 14,  # 7 points
            "constitution": 13,  # 5 points
            "intelligence": 12,  # 4 points
            "wisdom": 10,  # 2 points
            "charisma": 8,  # 0 points = 27 total
        }
        # Must pass initial to set up point_buy choices (form checks initial for method)
        form = AbilityScoreForm(data=data, initial={"generation_method": "point_buy"})
        assert form.is_valid(), form.errors

    def test_point_buy_exceeds_limit_rejected(self):
        """Point buy exceeding 27 points is rejected."""
        # All unique values, total = 9+7+5+4+3+2 = 30 points > 27
        data = {
            "generation_method": "point_buy",
            "strength": 15,  # 9 points
            "dexterity": 14,  # 7 points
            "constitution": 13,  # 5 points
            "intelligence": 12,  # 4 points
            "wisdom": 11,  # 3 points
            "charisma": 10,  # 2 points = 30 total > 27
        }
        # Must pass initial to set up point_buy choices (form checks initial for method)
        form = AbilityScoreForm(data=data, initial={"generation_method": "point_buy"})
        assert not form.is_valid()
        assert "Point buy total" in str(form.errors)

    def test_roll_method_allows_higher_scores(self):
        """Roll method allows scores up to 18."""
        data = {
            "generation_method": "roll",
            "strength": 18,
            "dexterity": 16,
            "constitution": 14,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
        }
        # Initialize with proper data to set up roll choices
        form = AbilityScoreForm(data=data, initial={"generation_method": "roll"})
        assert form.is_valid(), form.errors

    def test_generation_methods_available(self):
        form = AbilityScoreForm()
        choices = dict(form.fields["generation_method"].choices)
        assert "standard" in choices
        assert "point_buy" in choices
        assert "roll" in choices


class TestBackgroundSelectForm:
    def test_form_has_background_field(self):
        form = BackgroundSelectForm()
        assert "background" in form.fields

    def test_valid_form_with_background(self):
        form = BackgroundSelectForm(data={"background": Background.ACOLYTE})
        assert form.is_valid(), form.errors

    def test_invalid_without_background(self):
        form = BackgroundSelectForm(data={"background": ""})
        assert not form.is_valid()
        assert "background" in form.errors

    def test_get_background_preview_data_returns_dict(self):
        form = BackgroundSelectForm()
        preview_data = form.get_background_preview_data()
        assert isinstance(preview_data, dict)

    def test_all_backgrounds_in_choices(self):
        form = BackgroundSelectForm()
        choice_values = [c[0] for c in form.fields["background"].choices]
        for bg_value, _ in Background.choices:
            assert bg_value in choice_values


class TestGetSkillsHelper:
    def test_cleric_skills(self):
        skills = _get_skills(ClassName.CLERIC)
        assert skills is not None
        skill_values = {s[0] for s in skills}
        assert SkillName.HISTORY in skill_values
        assert SkillName.INSIGHT in skill_values
        assert SkillName.MEDICINE in skill_values
        assert SkillName.PERSUASION in skill_values
        assert SkillName.RELIGION in skill_values

    def test_fighter_skills(self):
        skills = _get_skills(ClassName.FIGHTER)
        assert skills is not None
        skill_values = {s[0] for s in skills}
        assert SkillName.ATHLETICS in skill_values
        assert SkillName.INTIMIDATION in skill_values
        assert SkillName.PERCEPTION in skill_values

    def test_rogue_skills(self):
        skills = _get_skills(ClassName.ROGUE)
        assert skills is not None
        skill_values = {s[0] for s in skills}
        assert SkillName.STEALTH in skill_values
        assert SkillName.SLEIGHT_OF_HAND in skill_values
        assert SkillName.DECEPTION in skill_values

    def test_wizard_skills(self):
        skills = _get_skills(ClassName.WIZARD)
        assert skills is not None
        skill_values = {s[0] for s in skills}
        assert SkillName.ARCANA in skill_values
        assert SkillName.INVESTIGATION in skill_values

    def test_unknown_class_returns_none(self):
        skills = _get_skills("unknown_class")
        assert skills is None


class TestGetNumSkillsHelper:
    def test_rogue_gets_four_skills(self):
        assert _get_num_skills(ClassName.ROGUE) == 4

    def test_bard_gets_three_skills(self):
        assert _get_num_skills(ClassName.BARD) == 3

    def test_other_classes_get_two_skills(self):
        assert _get_num_skills(ClassName.FIGHTER) == 2
        assert _get_num_skills(ClassName.CLERIC) == 2
        assert _get_num_skills(ClassName.WIZARD) == 2


class TestSkillsSelectForm:
    def test_form_fields_based_on_class(self):
        klass = ClassFactory(name=ClassName.FIGHTER)
        form = SkillsSelectForm(initial={"klass": klass})
        # Fighter gets 2 skills
        assert "first_skill" in form.fields
        assert "second_skill" in form.fields
        assert "third_skill" not in form.fields

    def test_rogue_gets_four_skill_fields(self):
        klass = ClassFactory(name=ClassName.ROGUE)
        form = SkillsSelectForm(initial={"klass": klass})
        assert "first_skill" in form.fields
        assert "second_skill" in form.fields
        assert "third_skill" in form.fields
        assert "fourth_skill" in form.fields

    def test_form_without_class_has_no_fields(self):
        form = SkillsSelectForm()
        assert "first_skill" not in form.fields

    def test_valid_skill_selection(self):
        klass = ClassFactory(name=ClassName.FIGHTER)
        form = SkillsSelectForm(
            data={
                "first_skill": SkillName.ATHLETICS,
                "second_skill": SkillName.PERCEPTION,
            },
            initial={"klass": klass},
        )
        assert form.is_valid(), form.errors

    def test_duplicate_skills_rejected(self):
        klass = ClassFactory(name=ClassName.FIGHTER)
        form = SkillsSelectForm(
            data={
                "first_skill": SkillName.ATHLETICS,
                "second_skill": SkillName.ATHLETICS,  # Duplicate
            },
            initial={"klass": klass},
        )
        assert not form.is_valid()


class TestEquipmentSelectForm:
    def test_cleric_equipment_fields(self):
        klass = ClassFactory(name=ClassName.CLERIC)
        form = EquipmentSelectForm(initial={"klass": klass})
        # Cleric should have these fields
        assert "first_weapon" in form.fields or "armor" in form.fields

    def test_fighter_equipment_fields(self):
        klass = ClassFactory(name=ClassName.FIGHTER)
        form = EquipmentSelectForm(initial={"klass": klass})
        # Fighter should have weapon choices
        assert len(form.fields) > 0

    def test_rogue_equipment_fields(self):
        klass = ClassFactory(name=ClassName.ROGUE)
        form = EquipmentSelectForm(initial={"klass": klass})
        # Rogue should have weapon and pack choices
        assert len(form.fields) > 0

    def test_form_without_class_has_no_fields(self):
        form = EquipmentSelectForm()
        assert len(form.fields) == 0


class TestReviewForm:
    def test_form_has_name_field(self):
        form = ReviewForm()
        assert "name" in form.fields
        assert form.fields["name"].max_length == 50

    def test_valid_form_with_unique_name(self):
        form = ReviewForm(data={"name": "Aragorn"})
        assert form.is_valid(), form.errors

    def test_duplicate_character_name_rejected(self):
        CharacterFactory(name="Gandalf")
        form = ReviewForm(data={"name": "Gandalf"})
        assert not form.is_valid()
        assert "name" in form.errors
        assert "already exists" in str(form.errors["name"])

    def test_empty_name_rejected(self):
        form = ReviewForm(data={"name": ""})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_name_too_long_rejected(self):
        form = ReviewForm(data={"name": "x" * 51})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_get_character_summary_returns_dict(self):
        form = ReviewForm(wizard_data={})
        summary = form.get_character_summary()
        assert isinstance(summary, dict)

    def test_get_character_summary_with_species_data(self):
        species = SpeciesFactory()
        wizard_data = {"0": {"species": species.pk}}
        form = ReviewForm(wizard_data=wizard_data)
        summary = form.get_character_summary()
        assert "species" in summary
        assert summary["species"]["speed"] == species.speed

    def test_get_character_summary_with_class_data(self):
        klass = ClassFactory()
        wizard_data = {"1": {"klass": klass.pk}}
        form = ReviewForm(wizard_data=wizard_data)
        summary = form.get_character_summary()
        assert "klass" in summary
        assert f"d{klass.hit_die}" in summary["klass"]["hit_die"]

    def test_get_character_summary_with_abilities_data(self):
        wizard_data = {
            "2": {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            }
        }
        form = ReviewForm(wizard_data=wizard_data)
        summary = form.get_character_summary()
        assert "abilities" in summary
        assert summary["abilities"]["strength"] == 15

    def test_get_character_summary_with_background_data(self):
        wizard_data = {"3": {"background": Background.ACOLYTE}}
        form = ReviewForm(wizard_data=wizard_data)
        summary = form.get_character_summary()
        assert "background" in summary
