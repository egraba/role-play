import pytest

from game.constants.log_categories import LogCategory
from game.presenters import format_event_message
from game.serializers import serialize_game_log_event
from game.tests.factories import (
    DiceRollFactory,
    GameFactory,
    MessageFactory,
    PlayerFactory,
)


@pytest.mark.django_db
class TestSerializeGameLogEvent:
    def test_serialize_master_message_is_dm_category(self):
        game = GameFactory()
        master = game.master
        message = MessageFactory(game=game, author=master, content="Hello world")

        data = serialize_game_log_event(message)

        assert data["id"] == message.id
        assert data["type"] == "message"
        assert data["category"] == LogCategory.DM
        assert data["message"] == format_event_message(message)
        assert data["author_name"] == master.user.username
        assert "date" in data

    def test_serialize_player_message_is_chat_category(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        message = MessageFactory(game=game, author=player, content="Player says hi")

        data = serialize_game_log_event(message)

        assert data["category"] == LogCategory.CHAT
        assert data["character_id"] == player.character.id
        assert data["character_name"] == player.character.name

    def test_serialize_dice_roll_includes_details(self):
        game = GameFactory()
        master = game.master
        roll = DiceRollFactory(
            game=game,
            author=master,
            dice_notation="2d6",
            num_dice=2,
            modifier=3,
            individual_rolls=[4, 5],
            total=12,
            roll_purpose="damage",
        )

        data = serialize_game_log_event(roll)

        assert data["category"] == LogCategory.ROLLS
        assert data["details"] is not None
        assert data["details"]["dice_notation"] == "2d6"
        assert data["details"]["individual_rolls"] == [4, 5]
        assert data["details"]["modifier"] == 3
        assert data["details"]["total"] == 12
        assert data["details"]["roll_purpose"] == "damage"

    def test_serialize_plain_message_has_no_details(self):
        game = GameFactory()
        master = game.master
        message = MessageFactory(game=game, author=master, content="Just chatting")

        data = serialize_game_log_event(message)

        assert data["details"] is None
