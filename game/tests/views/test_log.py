import pytest
from django.urls import reverse

from game.tests.factories import (
    GameFactory,
    MessageFactory,
    PlayerFactory,
)


@pytest.mark.django_db
class TestGameLogView:
    def test_returns_recent_events(self, client):
        game = GameFactory()
        master = game.master

        for i in range(5):
            MessageFactory(game=game, author=master, content=f"Message {i}")

        client.force_login(master.user)
        url = reverse("game-log", kwargs={"game_id": game.id})
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert len(data["events"]) == 5

    def test_returns_max_50_events(self, client):
        game = GameFactory()
        master = game.master

        for i in range(60):
            MessageFactory(game=game, author=master, content=f"Message {i}")

        client.force_login(master.user)
        url = reverse("game-log", kwargs={"game_id": game.id})
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 50

    def test_returns_characters_in_game(self, client):
        game = GameFactory()
        master = game.master
        player = PlayerFactory(game=game)

        client.force_login(master.user)
        url = reverse("game-log", kwargs={"game_id": game.id})
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert "characters" in data
        assert len(data["characters"]) == 1
        assert data["characters"][0]["id"] == player.character.id
        assert data["characters"][0]["name"] == player.character.name

    def test_requires_authentication(self, client):
        game = GameFactory()
        url = reverse("game-log", kwargs={"game_id": game.id})
        response = client.get(url)

        assert response.status_code == 302
