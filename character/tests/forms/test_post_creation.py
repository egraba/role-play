import pytest
from django import forms

from character.forms.post_creation import SelectEquipmentForm
from character.models.classes import Class


@pytest.mark.django_db
class TestSelectEquipmentForm:
    form = None

    @pytest.fixture
    def cleric(self):
        self.form = SelectEquipmentForm(initial={"class_name": Class.CLERIC})

    def test_weapon1_field_exists(self, cleric):
        assert "weapon1" in self.form.fields

    def test_weapon1_field_type(self, cleric):
        assert isinstance(self.form.fields["weapon1"], forms.ChoiceField)

    def test_amor_field_exists(self, cleric):
        assert "armor" in self.form.fields

    def test_armor_field_type(self, cleric):
        assert isinstance(self.form.fields["armor"], forms.ChoiceField)

    def test_weapon2_field_exists(self, cleric):
        assert "weapon2" in self.form.fields

    def test_weapon2_field_type(self, cleric):
        assert isinstance(self.form.fields["weapon2"], forms.ChoiceField)

    def test_pack_field_exists(self, cleric):
        assert "pack" in self.form.fields

    def test_pack_field_type(self, cleric):
        assert isinstance(self.form.fields["pack"], forms.ChoiceField)
