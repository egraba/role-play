from django import forms

from character.forms.character import CharacterCreateForm
from game.forms import QuestCreateForm


class TestQuestCreateForm:
    def test_content_type(self):
        form = QuestCreateForm()
        assert isinstance(form.fields["content"].widget, forms.Textarea)

    def test_content_max_length(self):
        form = QuestCreateForm()
        assert form.fields["content"].max_length == 1000


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
