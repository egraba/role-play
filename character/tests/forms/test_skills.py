import pytest
from django import forms

from character.constants.klasses import Klass
from character.forms.skills import SkillsSelectForm


@pytest.fixture
def cleric_form():
    return SkillsSelectForm(initial={"klass": Klass.CLERIC})


@pytest.fixture
def cleric_fields():
    return ["first_skill", "second_skill"]


def test_cleric_fields_presence(cleric_form, cleric_fields):
    assert cleric_fields == list(cleric_form.fields)


def test_cleric_fields_type(cleric_form):
    for field in cleric_form.fields:
        assert isinstance(cleric_form.fields[field], forms.ChoiceField)


@pytest.fixture
def fighter_form():
    return SkillsSelectForm(initial={"klass": Klass.FIGHTER})


@pytest.fixture
def fighter_fields():
    return ["first_skill", "second_skill"]


def test_fighter_fields_presence(fighter_form, fighter_fields):
    assert fighter_fields == list(fighter_form.fields)


def test_fighter_fields_type(fighter_form):
    for field in fighter_form.fields:
        assert isinstance(fighter_form.fields[field], forms.ChoiceField)


@pytest.fixture
def rogue_form():
    return SkillsSelectForm(initial={"klass": Klass.ROGUE})


@pytest.fixture
def rogue_fields():
    return ["first_skill", "second_skill", "third_skill", "fourth_skill"]


def test_rogue_fields_presence(rogue_form, rogue_fields):
    assert rogue_fields == list(rogue_form.fields)


def test_rogue_fields_type(rogue_form):
    for field in rogue_form.fields:
        assert isinstance(rogue_form.fields[field], forms.ChoiceField)


@pytest.fixture
def wizard_form():
    return SkillsSelectForm(initial={"klass": Klass.WIZARD})


@pytest.fixture
def wizard_fields():
    return ["first_skill", "second_skill"]


def test_wizard_fields_presence(wizard_form, wizard_fields):
    assert wizard_fields == list(wizard_form.fields)


def test_wizard_fields_type(wizard_form):
    for field in wizard_form.fields:
        assert isinstance(wizard_form.fields[field], forms.ChoiceField)
