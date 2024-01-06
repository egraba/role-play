import pytest
from django import forms

from character.forms.equipment_selection import (
    ClericEquipmentSelectForm,
    FighterEquipmentSelectForm,
    RogueEquipmentSelectForm,
    WizardEquipmentSelectForm,
)


@pytest.mark.django_db
class TestClericEquipmentSelectForm:
    form = None

    @pytest.fixture
    def cleric(self):
        self.form = ClericEquipmentSelectForm()

    def test_first_weapon_field_exists_for_cleric(self, cleric):
        assert "first_weapon" in self.form.fields

    def test_first_weapon_field_type_for_cleric(self, cleric):
        assert isinstance(self.form.fields["first_weapon"], forms.ChoiceField)

    def test_amor_field_exists_for_cleric(self, cleric):
        assert "armor" in self.form.fields

    def test_armor_field_type_for_cleric(self, cleric):
        assert isinstance(self.form.fields["armor"], forms.ChoiceField)

    def test_second_weapon_field_exists_for_cleric(self, cleric):
        assert "second_weapon" in self.form.fields

    def test_second_weapon_field_type_for_cleric(self, cleric):
        assert isinstance(self.form.fields["second_weapon"], forms.ChoiceField)

    def test_third_weapon_field_does_not_exist_for_cleric(self, cleric):
        assert "third_weapon" not in self.form.fields

    def test_pack_field_exists_for_cleric(self, cleric):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_cleric(self, cleric):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    def test_field_order(self, cleric):
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

    @pytest.fixture
    def fighter(self):
        self.form = FighterEquipmentSelectForm()

    def test_first_weapon_field_exists_for_fighter(self, fighter):
        assert "first_weapon" in self.form.fields

    def test_first_weapon_field_type_for_fighter(self, fighter):
        assert isinstance(self.form.fields["first_weapon"], forms.ChoiceField)

    def test_amor_field_does_not_exist_for_fighter(self, fighter):
        assert "armor" not in self.form.fields

    def test_second_weapon_field_exists_for_fighter(self, fighter):
        assert "second_weapon" in self.form.fields

    def test_second_weapon_field_type_for_fighter(self, fighter):
        assert isinstance(self.form.fields["second_weapon"], forms.ChoiceField)

    def test_third_weapon_field_exists_for_fighter(self, fighter):
        assert "third_weapon" in self.form.fields

    def test_third_weapon_field_type_for_fighter(self, fighter):
        assert isinstance(self.form.fields["third_weapon"], forms.ChoiceField)

    def test_pack_field_exists_for_fighter(self, fighter):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_fighter(self, fighter):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    def test_field_order(self, fighter):
        assert list(self.form.fields.keys()) == [
            "first_weapon",
            "second_weapon",
            "third_weapon",
            "pack",
        ]


@pytest.mark.django_db
class TestRogueEquipmentSelectForm:
    form = None

    @pytest.fixture
    def rogue(self):
        self.form = RogueEquipmentSelectForm()

    def test_first_weapon_field_exists_for_rogue(self, rogue):
        assert "first_weapon" in self.form.fields

    def test_first_weapon_field_type_for_rogue(self, rogue):
        assert isinstance(self.form.fields["first_weapon"], forms.ChoiceField)

    def test_amor_field_does_not_exist_for_rogue(self, rogue):
        assert "armor" not in self.form.fields

    def test_second_weapon_field_exists_for_rogue(self, rogue):
        assert "second_weapon" in self.form.fields

    def test_second_weapon_field_type_for_rogue(self, rogue):
        assert isinstance(self.form.fields["second_weapon"], forms.ChoiceField)

    def test_third_weapon_field_does_not_exist_for_rogue(self, rogue):
        assert "third_weapon" not in self.form.fields

    def test_pack_field_exists_for_rogue(self, rogue):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_rogue(self, rogue):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    def test_field_order(self, rogue):
        assert list(self.form.fields.keys()) == [
            "first_weapon",
            "second_weapon",
            "pack",
        ]


@pytest.mark.django_db
class TestWizardEquipmentSelectForm:
    form = None

    @pytest.fixture
    def wizard(self):
        self.form = WizardEquipmentSelectForm()

    def test_first_weapon_field_exists_for_wizard(self, wizard):
        assert "first_weapon" in self.form.fields

    def test_first_weapon_field_type_for_wizard(self, wizard):
        assert isinstance(self.form.fields["first_weapon"], forms.ChoiceField)

    def test_amor_field_does_not_exist_for_wizard(self, wizard):
        assert "armor" not in self.form.fields

    def test_second_weapon_field_does_not_exist_for_wizard(self, wizard):
        assert "second_weapon" not in self.form.fields

    def test_third_weapon_field_does_not_exist_for_wizard(self, wizard):
        assert "third_weapon" not in self.form.fields

    def test_pack_field_exists_for_wizard(self, wizard):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_wizard(self, wizard):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    def test_gear_field_exists_for_wizard(self, wizard):
        assert "gear" in self.form.fields

    def test_gear_field_type_for_wizard(self, wizard):
        assert isinstance(self.form.fields["gear"], forms.ChoiceField)

    def test_field_order(self, wizard):
        assert list(self.form.fields.keys()) == [
            "first_weapon",
            "gear",
            "pack",
        ]
