import pytest
from django import forms

from character.constants.abilities import AbilityName
from character.models.character import Character
from game.constants.combat import FighterAttributeChoices
from game.flows import GameFlow
from game.forms import AbilityCheckRequestForm, CombatCreateForm, QuestCreateForm
from game.models.game import Player

from .factories import GameFactory, PlayerFactory


class TestQuestCreateForm:
    def test_environment_type(self):
        form = QuestCreateForm()
        assert isinstance(form.fields["environment"].widget, forms.Textarea)

    def test_environment_max_length(self):
        form = QuestCreateForm()
        assert form.fields["environment"].max_length == 3000


pytestmark = pytest.mark.django_db


class TestAbilityCheckRequestForm:
    @pytest.fixture
    def game_with_players(self):
        game = GameFactory()
        PlayerFactory(game=game)
        PlayerFactory(game=game)
        flow = GameFlow(game)
        flow.start()
        return game

    def test_player_field_uses_player_queryset(self, game_with_players):
        form = AbilityCheckRequestForm(initial={"game": game_with_players})
        players = Player.objects.filter(game=game_with_players)
        assert list(form.fields["player"].queryset) == list(players)

    def test_player_field_displays_username(self, game_with_players):
        form = AbilityCheckRequestForm(initial={"game": game_with_players})
        player = form.fields["player"].queryset.first()
        # The queryset uses Player model which has __str__ returning username
        assert str(player) == player.user.username

    def test_ability_type_has_empty_choice(self, game_with_players):
        form = AbilityCheckRequestForm(initial={"game": game_with_players})
        choices = form.fields["ability_type"].choices
        assert choices[0] == ("", "---------")

    def test_ability_type_has_all_abilities(self, game_with_players):
        form = AbilityCheckRequestForm(initial={"game": game_with_players})
        choices = form.fields["ability_type"].choices
        # Skip empty choice
        ability_choices = choices[1:]
        assert ability_choices == list(AbilityName.choices)

    def test_player_field_widget_has_rpgui_dropdown_class(self, game_with_players):
        form = AbilityCheckRequestForm(initial={"game": game_with_players})
        widget = form.fields["player"].widget
        assert isinstance(widget, forms.Select)
        assert widget.attrs.get("class") == "rpgui-dropdown"

    def test_ability_type_widget_has_rpgui_dropdown_class(self, game_with_players):
        form = AbilityCheckRequestForm(initial={"game": game_with_players})
        widget = form.fields["ability_type"].widget
        assert isinstance(widget, forms.Select)
        assert widget.attrs.get("class") == "rpgui-dropdown"

    def test_difficulty_class_widget_has_rpgui_dropdown_class(self, game_with_players):
        form = AbilityCheckRequestForm(initial={"game": game_with_players})
        widget = form.fields["difficulty_class"].widget
        assert isinstance(widget, forms.Select)
        assert widget.attrs.get("class") == "rpgui-dropdown"

    def test_ability_type_label_is_ability(self, game_with_players):
        form = AbilityCheckRequestForm(initial={"game": game_with_players})
        assert form.fields["ability_type"].label == "Ability"

class TestCombatCreateForm:
    def test_character_fields(self, started_game):
        form = CombatCreateForm(initial={"game": f"{started_game.id}"})
        players = started_game.player_set.all()
        character_name_list = [player.character.name for player in players]
        assert list(form.fields.keys()) == character_name_list

    def test_form_valid_one_fighter(self, started_game):
        characters = Character.objects.filter(player__game=started_game)
        data = {}
        data[characters.first().name] = [FighterAttributeChoices.IS_FIGHTING]
        form = CombatCreateForm(data, initial={"game": f"{started_game.id}"})
        assert form.is_valid()

    def test_form_invalid_no_fighters(self, started_game):
        form = CombatCreateForm(initial={"game": f"{started_game.id}"})
        assert not form.is_valid()

    def test_form_invalid_surprised_non_fighter(self, started_game):
        characters = Character.objects.filter(player__game=started_game)
        data = {}
        data[characters.first().name] = [FighterAttributeChoices.IS_SURPRISED]
        form = CombatCreateForm(initial={"game": f"{started_game.id}"})
        assert not form.is_valid()
