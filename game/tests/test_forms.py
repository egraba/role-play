from django import forms

from character.forms.character import CharacterCreateForm
from game.forms import (
    ChoiceForm,
    DamageForm,
    HealingForm,
    QuestCreateForm,
    XpIncreaseForm,
)


class TestQuestCreateForm:
    def test_content_type(self):
        form = QuestCreateForm()
        assert isinstance(form.fields["content"].widget, forms.Textarea)

    def test_content_max_length(self):
        form = QuestCreateForm()
        assert form.fields["content"].max_length == 1000


class TestXpIncreaseForm:
    def test_xp_type(self):
        form = XpIncreaseForm()
        assert isinstance(form.fields["xp"].widget, forms.NumberInput)


class TestDamageForm:
    def test_hp_type(self):
        form = DamageForm()
        assert isinstance(form.fields["hp"].widget, forms.NumberInput)


class TestHealingForm:
    def test_hp_type(self):
        form = HealingForm()
        assert isinstance(form.fields["hp"].widget, forms.NumberInput)


class TestCharacterCreateForm:
    def test_name_type(self):
        form = CharacterCreateForm()
        assert isinstance(form.fields["name"].widget, forms.TextInput)

    def test_name_max_length(self):
        form = CharacterCreateForm()
        assert form.fields["name"].max_length == 100

    def test_race_type(self):
        form = CharacterCreateForm()
        assert isinstance(form.fields["race"].widget, forms.Select)


class TestChoiceForm:
    def test_selection_type(self):
        form = ChoiceForm()
        assert isinstance(form.fields["selection"].widget, forms.Textarea)

    def test_name_max_length(self):
        form = ChoiceForm()
        assert form.fields["selection"].max_length == 50
