import pytest
from django import forms

from game.forms import CombatCreateForm, QuestCreateForm


class TestQuestCreateForm:
    def test_content_type(self):
        form = QuestCreateForm()
        assert isinstance(form.fields["content"].widget, forms.Textarea)

    def test_content_max_length(self):
        form = QuestCreateForm()
        assert form.fields["content"].max_length == 1000


pytestmark = pytest.mark.django_db


class TestCombatCreateForm:
    def test_character_fields(self, started_game):
        form = CombatCreateForm(initial={"game": f"{started_game.id}"})
        players = started_game.player_set.all()
        character_name_list = [player.character.name for player in players]
        assert list(form.fields.keys()) == character_name_list

    def test_form_invalid_no_fighters(self, started_game):
        form = CombatCreateForm(initial={"game": f"{started_game.id}"})
        assert not form.is_valid()
