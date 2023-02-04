from django import forms
from django.test import TestCase

from game.forms import NewGameForm


class NewGameFormTest(TestCase):
    def test_name_type(self):
        form = NewGameForm()
        self.assertIsInstance(form.fields["name"].widget, forms.TextInput)

    def test_name_max_length(self):
        form = NewGameForm()
        self.assertEqual(form.fields["name"].max_length, 255)
