from django import forms
from django.test import TestCase

from game.forms import (
    ChoiceForm,
    CreateGameForm,
    CreateTaleForm,
    DamageForm,
    HealForm,
    IncreaseXpForm,
)


class CreateGameFormTest(TestCase):
    def test_name_type(self):
        form = CreateGameForm()
        self.assertIsInstance(form.fields["name"].widget, forms.TextInput)

    def test_name_max_length(self):
        form = CreateGameForm()
        self.assertEqual(form.fields["name"].max_length, 50)

    def test_description_type(self):
        form = CreateTaleForm()
        self.assertIsInstance(form.fields["description"].widget, forms.Textarea)

    def test_description_max_length(self):
        form = CreateTaleForm()
        self.assertEqual(form.fields["description"].max_length, 1000)


class CreateTaleFormTest(TestCase):
    def test_description_type(self):
        form = CreateTaleForm()
        self.assertIsInstance(form.fields["description"].widget, forms.Textarea)

    def test_description_max_length(self):
        form = CreateTaleForm()
        self.assertEqual(form.fields["description"].max_length, 1000)


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


class ChoiceFormTest(TestCase):
    def test_selection_type(self):
        form = ChoiceForm()
        self.assertIsInstance(form.fields["selection"].widget, forms.Textarea)

    def test_name_max_length(self):
        form = ChoiceForm()
        self.assertEqual(form.fields["selection"].max_length, 300)
