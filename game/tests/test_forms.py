from django import forms
from django.test import TestCase

from character.forms.character import CreateCharacterForm
from game.forms import ChoiceForm, CreateQuestForm, DamageForm, HealForm, IncreaseXpForm


class CreateQuestFormTest(TestCase):
    def test_content_type(self):
        form = CreateQuestForm()
        self.assertIsInstance(form.fields["content"].widget, forms.Textarea)

    def test_content_max_length(self):
        form = CreateQuestForm()
        self.assertEqual(form.fields["content"].max_length, 1000)


class IncreaseXpFormTest(TestCase):
    def test_xp_type(self):
        form = IncreaseXpForm()
        self.assertIsInstance(form.fields["xp"].widget, forms.NumberInput)


class DamageFormTest(TestCase):
    def test_hp_type(self):
        form = DamageForm()
        self.assertIsInstance(form.fields["hp"].widget, forms.NumberInput)


class HealFormTest(TestCase):
    def test_hp_type(self):
        form = HealForm()
        self.assertIsInstance(form.fields["hp"].widget, forms.NumberInput)


class CreateCharacterFormTest(TestCase):
    def test_name_type(self):
        form = CreateCharacterForm()
        self.assertIsInstance(form.fields["name"].widget, forms.TextInput)

    def test_name_max_length(self):
        form = CreateCharacterForm()
        self.assertEqual(form.fields["name"].max_length, 100)

    def test_race_type(self):
        form = CreateCharacterForm()
        self.assertIsInstance(form.fields["race"].widget, forms.Select)


class ChoiceFormTest(TestCase):
    def test_selection_type(self):
        form = ChoiceForm()
        self.assertIsInstance(form.fields["selection"].widget, forms.Textarea)

    def test_name_max_length(self):
        form = ChoiceForm()
        self.assertEqual(form.fields["selection"].max_length, 50)
