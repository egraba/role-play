from django import forms
from django.test import TestCase

import character.forms as cforms
import game.forms as gforms


class CreateQuestFormTest(TestCase):
    def test_content_type(self):
        form = gforms.CreateQuestForm()
        self.assertIsInstance(form.fields["content"].widget, forms.Textarea)

    def test_content_max_length(self):
        form = gforms.CreateQuestForm()
        self.assertEqual(form.fields["content"].max_length, 1000)


class IncreaseXpFormTest(TestCase):
    def test_xp_type(self):
        form = gforms.IncreaseXpForm()
        self.assertIsInstance(form.fields["xp"].widget, forms.NumberInput)


class DamageFormTest(TestCase):
    def test_hp_type(self):
        form = gforms.DamageForm()
        self.assertIsInstance(form.fields["hp"].widget, forms.NumberInput)


class HealFormTest(TestCase):
    def test_hp_type(self):
        form = gforms.HealForm()
        self.assertIsInstance(form.fields["hp"].widget, forms.NumberInput)


class CreateCharacterFormTest(TestCase):
    def test_name_type(self):
        form = cforms.CreateCharacterForm()
        self.assertIsInstance(form.fields["name"].widget, forms.TextInput)

    def test_name_max_length(self):
        form = cforms.CreateCharacterForm()
        self.assertEqual(form.fields["name"].max_length, 100)

    def test_race_type(self):
        form = cforms.CreateCharacterForm()
        self.assertIsInstance(form.fields["race"].widget, forms.Select)


class ChoiceFormTest(TestCase):
    def test_selection_type(self):
        form = gforms.ChoiceForm()
        self.assertIsInstance(form.fields["selection"].widget, forms.Textarea)

    def test_name_max_length(self):
        form = gforms.ChoiceForm()
        self.assertEqual(form.fields["selection"].max_length, 50)
