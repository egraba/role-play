import pytest
from django import forms

from character.forms.equipment import EquipmentSelectForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def form():
    return EquipmentSelectForm


@pytest.fixture
def cleric_fields():
    return ["first_weapon", "second_weapon", "armor", "gear", "pack"]


def test_cleric_fields_presence(form, cleric_fields):
    assert cleric_fields == form.fields


def test_cleric_fields_type(form, cleric_fields):
    for field in cleric_fields:
        assert isinstance(field, forms.ChoiceField)


@pytest.fixture
def fighter_fields():
    return ["first_weapon", "second_weapon", "third_weapon", "pack"]


def test_fighter_fields_presence(form, fighter_fields):
    assert fighter_fields == form.fields


def test_fighter_fields_type(form, fighter_fields):
    for field in fighter_fields:
        assert isinstance(field, forms.ChoiceField)


@pytest.fixture
def rogue_fields():
    return ["first_weapon", "second_weapon", "pack"]


def test_rogue_fields_presence(form, rogue_fields):
    assert rogue_fields == form.fields


def test_rogue_fields_type(form, rogue_fields):
    for field in rogue_fields:
        assert isinstance(field, forms.ChoiceField)


@pytest.fixture
def wizard_fields():
    return ["first_weapon", "gear", "pack"]


def test_wizard_fields_presence(form, wizard_fields):
    assert wizard_fields == form.fields


def test_wizard_fields_type(form, wizard_fields):
    for field in wizard_fields:
        assert isinstance(field, forms.ChoiceField)
