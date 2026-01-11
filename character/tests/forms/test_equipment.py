import pytest
from django import forms

from character.models.klasses import Klass
from character.forms.equipment import EquipmentSelectForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def cleric_form():
    return EquipmentSelectForm(initial={"klass": Klass.CLERIC})


def test_cleric_fields_presence(cleric_form):
    assert list(cleric_form.fields) == [
        "first_weapon",
        "second_weapon",
        "armor",
        "gear",
        "pack",
    ]


def test_cleric_fields_type(cleric_form):
    for field in cleric_form.fields:
        assert isinstance(cleric_form.fields[field], forms.ChoiceField)


@pytest.fixture
def fighter_form():
    return EquipmentSelectForm(initial={"klass": Klass.FIGHTER})


def test_fighter_fields_presence(fighter_form):
    assert list(fighter_form.fields) == [
        "first_weapon",
        "second_weapon",
        "third_weapon",
        "pack",
    ]


def test_fighter_fields_type(fighter_form):
    for field in fighter_form.fields:
        assert isinstance(fighter_form.fields[field], forms.ChoiceField)


@pytest.fixture
def rogue_form():
    return EquipmentSelectForm(initial={"klass": Klass.ROGUE})


def test_rogue_fields_presence(rogue_form):
    assert list(rogue_form.fields) == ["first_weapon", "second_weapon", "pack"]


def test_rogue_fields_type(rogue_form):
    for field in rogue_form.fields:
        assert isinstance(rogue_form.fields[field], forms.ChoiceField)


@pytest.fixture
def wizard_form():
    return EquipmentSelectForm(initial={"klass": Klass.WIZARD})


def test_wizard_fields_presence(wizard_form):
    assert list(wizard_form.fields) == ["first_weapon", "gear", "pack"]


def test_wizard_fields_type(wizard_form):
    for field in wizard_form.fields:
        assert isinstance(wizard_form.fields[field], forms.ChoiceField)
