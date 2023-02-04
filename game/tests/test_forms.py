from django import forms
from django.test import TestCase

from game.forms import ChoiceForm, NewGameForm, NewNarrativeForm


class NewGameFormTest(TestCase):
    def test_name_type(self):
        form = NewGameForm()
        self.assertIsInstance(form.fields["name"].widget, forms.TextInput)

    def test_name_max_length(self):
        form = NewGameForm()
        self.assertEqual(form.fields["name"].max_length, 255)


class NewNarrativeFormTest(TestCase):
    def test_message_type(self):
        form = NewNarrativeForm()
        self.assertIsInstance(form.fields["message"].widget, forms.Textarea)

    def test_name_max_length(self):
        form = NewNarrativeForm()
        self.assertEqual(form.fields["message"].max_length, 1024)


class ChoiceFormTest(TestCase):
    def test_selection_type(self):
        form = ChoiceForm()
        self.assertIsInstance(form.fields["selection"].widget, forms.Textarea)

    def test_name_max_length(self):
        form = ChoiceForm()
        self.assertEqual(form.fields["selection"].max_length, 255)
