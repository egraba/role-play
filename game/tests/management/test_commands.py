import pytest
from io import StringIO
from django.core.management import call_command

from game.models.combat import Combat
from game.models.game import Game

from ..factories import CombatFactory, GameFactory


pytestmark = pytest.mark.django_db


class TestDeleteCombatsCommand:
    """Tests for delete_combats management command."""

    def test_delete_combats_success(self):
        """Test successfully deleting combats from a game."""
        game = GameFactory()
        # Create combats for this game
        CombatFactory(game=game)
        CombatFactory(game=game)
        assert Combat.objects.filter(game=game).count() == 2

        out = StringIO()
        call_command("delete_combats", game.id, stdout=out)

        assert Combat.objects.filter(game=game).count() == 0
        assert "Successfully deleted" in out.getvalue()

    def test_delete_combats_multiple_games(self):
        """Test deleting combats from multiple games."""
        game1 = GameFactory()
        game2 = GameFactory()
        CombatFactory(game=game1)
        CombatFactory(game=game2)

        out = StringIO()
        call_command("delete_combats", game1.id, game2.id, stdout=out)

        assert Combat.objects.filter(game=game1).count() == 0
        assert Combat.objects.filter(game=game2).count() == 0

    def test_delete_combats_game_not_found(self):
        """Test error when game doesn't exist."""
        err = StringIO()
        with pytest.raises(Game.DoesNotExist):
            call_command("delete_combats", 99999, stderr=err)

        assert "not found" in err.getvalue()

    def test_delete_combats_no_combats(self):
        """Test deleting when no combats exist."""
        game = GameFactory()
        assert Combat.objects.filter(game=game).count() == 0

        out = StringIO()
        call_command("delete_combats", game.id, stdout=out)

        assert "Successfully deleted" in out.getvalue()
