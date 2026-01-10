import pytest

from character.forms.character import CharacterCreateForm


@pytest.fixture
def form():
    return CharacterCreateForm()


def test_name_field_exists(form):
    assert "name" in form.fields


def test_species_field_exists(form):
    assert "species" in form.fields


def test_klass_field_exists(form):
    assert "klass" in form.fields


def test_strength_field_exists(form):
    assert "strength" in form.fields


def test_dexterity_field_exists(form):
    assert "dexterity" in form.fields


def test_constitution_field_exists(form):
    assert "constitution" in form.fields


def test_intelligence_field_exists(form):
    assert "intelligence" in form.fields


def test_wisdom_field_exists(form):
    assert "wisdom" in form.fields


def test_charisma_field_exists(form):
    assert "charisma" in form.fields
