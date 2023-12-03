import pytest
from django import forms

from character.forms.post_creation import SelectEquipmentForm
from character.models.classes import Class


@pytest.mark.django_db
class TestSelectEquipmentForm:
    form = None

    @pytest.fixture
    def cleric(self, equipment):
        self.form = SelectEquipmentForm(initial={"class_name": Class.CLERIC})

    def test_weapon1_field_exists_for_cleric(self, cleric):
        assert "weapon1" in self.form.fields

    def test_weapon1_field_type_for_cleric(self, cleric):
        assert isinstance(self.form.fields["weapon1"], forms.ChoiceField)

    def test_amor_field_exists_for_cleric(self, cleric):
        assert "armor" in self.form.fields

    def test_armor_field_type_for_cleric(self, cleric):
        assert isinstance(self.form.fields["armor"], forms.ChoiceField)

    def test_weapon2_field_exists_for_cleric(self, cleric):
        assert "weapon2" in self.form.fields

    def test_weapon2_field_type_for_cleric(self, cleric):
        assert isinstance(self.form.fields["weapon2"], forms.ChoiceField)

    def test_weapon3_field_does_not_exist_for_cleric(self, cleric):
        assert "weapon3" not in self.form.fields

    def test_pack_field_exists_for_cleric(self, cleric):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_cleric(self, cleric):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    @pytest.fixture
    def fighter(self, equipment):
        self.form = SelectEquipmentForm(initial={"class_name": Class.FIGHTER})

    def test_weapon1_field_exists_for_fighter(self, fighter):
        assert "weapon1" in self.form.fields

    def test_weapon1_field_type_for_fighter(self, fighter):
        assert isinstance(self.form.fields["weapon1"], forms.ChoiceField)

    def test_amor_field_does_not_exist_for_fighter(self, fighter):
        assert "armor" not in self.form.fields

    def test_weapon2_field_exists_for_fighter(self, fighter):
        assert "weapon2" in self.form.fields

    def test_weapon2_field_type_for_fighter(self, fighter):
        assert isinstance(self.form.fields["weapon2"], forms.ChoiceField)

    def test_weapon3_field_exists_for_fighter(self, fighter):
        assert "weapon3" in self.form.fields

    def test_weapon3_field_type_for_fighter(self, fighter):
        assert isinstance(self.form.fields["weapon3"], forms.ChoiceField)

    def test_pack_field_exists_for_fighter(self, fighter):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_fighter(self, fighter):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    @pytest.fixture
    def rogue(self, equipment):
        self.form = SelectEquipmentForm(initial={"class_name": Class.ROGUE})

    def test_weapon1_field_exists_for_rogue(self, rogue):
        assert "weapon1" in self.form.fields

    def test_weapon1_field_type_for_rogue(self, rogue):
        assert isinstance(self.form.fields["weapon1"], forms.ChoiceField)

    def test_amor_field_does_not_exist_for_rogue(self, rogue):
        assert "armor" not in self.form.fields

    def test_weapon2_field_exists_for_rogue(self, rogue):
        assert "weapon2" in self.form.fields

    def test_weapon2_field_type_for_rogue(self, rogue):
        assert isinstance(self.form.fields["weapon2"], forms.ChoiceField)

    def test_weapon3_field_does_not_exist_for_rogue(self, rogue):
        assert "weapon3" not in self.form.fields

    def test_pack_field_exists_for_rogue(self, rogue):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_rogue(self, rogue):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    @pytest.fixture
    def wizard(self, equipment):
        self.form = SelectEquipmentForm(initial={"class_name": Class.WIZARD})

    def test_weapon1_field_exists_for_wizard(self, wizard):
        assert "weapon1" in self.form.fields

    def test_weapon1_field_type_for_wizard(self, wizard):
        assert isinstance(self.form.fields["weapon1"], forms.ChoiceField)

    def test_amor_field_does_not_exist_for_wizard(self, wizard):
        assert "armor" not in self.form.fields

    def test_weapon2_field_does_not_exist_for_wizard(self, wizard):
        assert "weapon2" not in self.form.fields

    def test_weapon3_field_does_not_exist_for_wizard(self, wizard):
        assert "weapon3" not in self.form.fields

    def test_pack_field_exists_for_wizard(self, wizard):
        assert "pack" in self.form.fields

    def test_pack_field_type_for_wizard(self, wizard):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)

    def test_gear_field_exists_for_wizard(self, wizard):
        assert "gear" in self.form.fields

    def test_gear_field_type_for_wizard(self, wizard):
        assert isinstance(self.form.fields["gear"], forms.ChoiceField)
