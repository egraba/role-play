import pytest

from game.constants.log_categories import LogCategory
from game.utils.channels import build_event_payload

from ..factories import (
    GameFactory,
    MessageFactory,
    PlayerFactory,
)


@pytest.mark.django_db
class TestBuildEventPayload:
    def test_includes_category_field(self):
        game = GameFactory()
        master = game.master
        message = MessageFactory(game=game, author=master, content="Test")

        payload = build_event_payload(message)

        assert "category" in payload
        assert payload["category"] == LogCategory.DM.value

    def test_includes_character_fields_for_player(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        message = MessageFactory(game=game, author=player, content="Test")

        payload = build_event_payload(message)

        assert payload["character_id"] == player.character.id
        assert payload["character_name"] == player.character.name
        assert payload["category"] == LogCategory.CHAT.value

    def test_master_has_no_character_fields(self):
        game = GameFactory()
        master = game.master
        message = MessageFactory(game=game, author=master, content="Test")

        payload = build_event_payload(message)

        assert payload["character_id"] is None
        assert payload["character_name"] is None
