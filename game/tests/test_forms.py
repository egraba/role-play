from django import forms
from django.test import TestCase

from game.forms import ChoiceForm, CreateGameForm, CreateTaleForm


class CreateGameFormTest(TestCase):
    def test_name_type(self):
        form = CreateGameForm()
        self.assertIsInstance(form.fields["name"].widget, forms.TextInput)

    def test_name_max_length(self):
        form = CreateGameForm()
        self.assertEqual(form.fields["name"].max_length, 50)


class CreateTaleFormTest(TestCase):
    def test_description_type(self):
        form = CreateTaleForm()
        self.assertIsInstance(form.fields["description"].widget, forms.Textarea)

    def test_description_max_length(self):
        form = CreateTaleForm()
        self.assertEqual(form.fields["description"].max_length, 1000)


class ChoiceFormTest(TestCase):
    def test_selection_type(self):
        form = ChoiceForm()
        self.assertIsInstance(form.fields["selection"].widget, forms.Textarea)

    def test_name_max_length(self):
        form = ChoiceForm()
        self.assertEqual(form.fields["selection"].max_length, 255)
