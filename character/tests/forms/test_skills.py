import pytest
from django import forms

from character.models.klasses import Klass
from character.forms.skills import SkillsSelectForm


@pytest.fixture
def cleric_form():
    return SkillsSelectForm(initial={"klass": Klass.CLERIC})


def test_cleric_fields_presence(cleric_form):
    assert list(cleric_form.fields) == ["first_skill", "second_skill"]


def test_cleric_fields_type(cleric_form):
    for field in cleric_form.fields:
        assert isinstance(cleric_form.fields[field], forms.ChoiceField)


@pytest.fixture
def fighter_form():
    return SkillsSelectForm(initial={"klass": Klass.FIGHTER})


def test_fighter_fields_presence(fighter_form):
    assert list(fighter_form.fields) == ["first_skill", "second_skill"]


def test_fighter_fields_type(fighter_form):
    for field in fighter_form.fields:
        assert isinstance(fighter_form.fields[field], forms.ChoiceField)


@pytest.fixture
def rogue_form():
    return SkillsSelectForm(initial={"klass": Klass.ROGUE})


def test_rogue_fields_presence(rogue_form):
    assert list(rogue_form.fields) == [
        "first_skill",
        "second_skill",
        "third_skill",
        "fourth_skill",
    ]


def test_rogue_fields_type(rogue_form):
    for field in rogue_form.fields:
        assert isinstance(rogue_form.fields[field], forms.ChoiceField)


@pytest.fixture
def wizard_form():
    return SkillsSelectForm(initial={"klass": Klass.WIZARD})


def test_wizard_fields_presence(wizard_form):
    assert list(wizard_form.fields) == ["first_skill", "second_skill"]


def test_wizard_fields_type(wizard_form):
    for field in wizard_form.fields:
        assert isinstance(wizard_form.fields[field], forms.ChoiceField)
