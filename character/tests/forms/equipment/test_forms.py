import pytest
from django import forms

from character.forms.equipment.equipment import (
    ClericEquipmentSelectForm,
    FighterEquipmentSelectForm,
    RogueEquipmentSelectForm,
    WizardEquipmentSelectForm,
)


@pytest.mark.django_db
class TestClericEquipmentSelectForm:
    form = None

    @pytest.fixture(autouse=True)
    def cleric(self):
        self.form = ClericEquipmentSelectForm()

    def test_first_weapon_field_exists_for_cleric(self):
        assert "first_weapon" in self.form.fields

    def test_first_weapon_field_type_for_cleric(self):
        assert isinstance(self.form.fields["first_weapon"], forms.ChoiceField)

    def test_amor_field_exists_for_cleric(self):
        assert "armor" in self.form.fields

    def test_armor_field_type_for_cleric(self):
        assert isinstance(self.form.fields["armor"], forms.ChoiceField)

    def test_second_weapon_field_exists_for_cleric(self):
        assert "second_weapon" in self.form.fields

    def test_second_weapon_field_type_for_cleric(self):
        assert isinstance(self.form.fields["second_weapon"], forms.ChoiceField)

    def test_third_weapon_field_does_not_exist_for_cleric(self):
        assert "third_weapon" not in self.form.fields

    def test_pack_field_exists_for_cleric(self):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_cleric(self):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    def test_field_order(self):
        assert list(self.form.fields.keys()) == [
            "first_weapon",
            "second_weapon",
            "armor",
            "gear",
            "pack",
        ]


@pytest.mark.django_db
class TestFighterEquipmentSelectForm:
    form = None

    @pytest.fixture(autouse=True)
    def fighter(self):
        self.form = FighterEquipmentSelectForm()

    def test_first_weapon_field_exists_for_fighter(self):
        assert "first_weapon" in self.form.fields

    def test_first_weapon_field_type_for_fighter(self):
        assert isinstance(self.form.fields["first_weapon"], forms.ChoiceField)

    def test_amor_field_does_not_exist_for_fighter(self):
        assert "armor" not in self.form.fields

    def test_second_weapon_field_exists_for_fighter(self):
        assert "second_weapon" in self.form.fields

    def test_second_weapon_field_type_for_fighter(self):
        assert isinstance(self.form.fields["second_weapon"], forms.ChoiceField)

    def test_third_weapon_field_exists_for_fighter(self):
        assert "third_weapon" in self.form.fields

    def test_third_weapon_field_type_for_fighter(self):
        assert isinstance(self.form.fields["third_weapon"], forms.ChoiceField)

    def test_pack_field_exists_for_fighter(self):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_fighter(self):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    def test_field_order(self):
        assert list(self.form.fields.keys()) == [
            "first_weapon",
            "second_weapon",
            "third_weapon",
            "pack",
        ]


@pytest.mark.django_db
class TestRogueEquipmentSelectForm:
    form = None

    @pytest.fixture(autouse=True)
    def rogue(self):
        self.form = RogueEquipmentSelectForm()

    def test_first_weapon_field_exists_for_rogue(self):
        assert "first_weapon" in self.form.fields

    def test_first_weapon_field_type_for_rogue(self):
        assert isinstance(self.form.fields["first_weapon"], forms.ChoiceField)

    def test_amor_field_does_not_exist_for_rogue(self):
        assert "armor" not in self.form.fields

    def test_second_weapon_field_exists_for_rogue(self):
        assert "second_weapon" in self.form.fields

    def test_second_weapon_field_type_for_rogue(self):
        assert isinstance(self.form.fields["second_weapon"], forms.ChoiceField)

    def test_third_weapon_field_does_not_exist_for_rogue(self):
        assert "third_weapon" not in self.form.fields

    def test_pack_field_exists_for_rogue(self):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_rogue(self):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    def test_field_order(self):
        assert list(self.form.fields.keys()) == [
            "first_weapon",
            "second_weapon",
            "pack",
        ]


@pytest.mark.django_db
class TestWizardEquipmentSelectForm:
    form = None

    @pytest.fixture(autouse=True)
    def wizard(self):
        self.form = WizardEquipmentSelectForm()

    def test_first_weapon_field_exists_for_wizard(self):
        assert "first_weapon" in self.form.fields

    def test_first_weapon_field_type_for_wizard(self):
        assert isinstance(self.form.fields["first_weapon"], forms.ChoiceField)

    def test_amor_field_does_not_exist_for_wizard(self):
        assert "armor" not in self.form.fields

    def test_second_weapon_field_does_not_exist_for_wizard(self):
        assert "second_weapon" not in self.form.fields

    def test_third_weapon_field_does_not_exist_for_wizard(self):
        assert "third_weapon" not in self.form.fields

    def test_pack_field_exists_for_wizard(self):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_wizard(self):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    def test_gear_field_exists_for_wizard(self):
        assert "gear" in self.form.fields

    def test_gear_field_type_for_wizard(self):
        assert isinstance(self.form.fields["gear"], forms.ChoiceField)

    def test_field_order(self):
        assert list(self.form.fields.keys()) == [
            "first_weapon",
            "gear",
            "pack",
        ]
