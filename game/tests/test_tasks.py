from difflib import SequenceMatcher

import pytest
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from faker import Faker

from character.models.character import Character
from game.models.events import Roll, RollRequest
from game.models.game import Game
from game.tasks import process_roll

from .factories import RollRequestFactory


@pytest.mark.django_db(transaction=True)
class TestProcessRoll:
    @pytest.fixture
    def ability_check_request(self):
        return RollRequestFactory(roll_type=RollRequest.RollType.ABILITY_CHECK)

    @pytest.fixture
    def game(self):
        # Retrieved from RollRequestFactory.
        return Game.objects.last()

    @pytest.fixture
    def character(self):
        # Retrieved from RollRequestFactory.
        return Character.objects.last()

    def test_ability_check_success(
        self, celery_worker, ability_check_request, game, character
    ):
        fake = Faker()
        date = timezone.now()
        message = fake.text(100)
        process_roll.delay(
            game_id=game.id,
            roll_type=RollRequest.RollType.ABILITY_CHECK,
            date=date.isoformat(),
            character_id=character.id,
            message=message,
        ).get()

        assert character.player.game == game

        roll = Roll.objects.last()
        assert roll.game == game
        assert (roll.date.second - date.second) <= 2
        # SequenceMatcher is used as the score is a random value, and therefore
        # cannot be guessed.
        expected_str = f"[{character.user}]'s score: 5, \
            {RollRequest.RollType.ABILITY_CHECK} result: {roll.get_result_display()}"
        s = SequenceMatcher(None, roll.message, expected_str)
        assert s.ratio() > 0.9

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollRequest.Status.DONE

    def test_roll_failure_game_not_found(
        self, celery_worker, ability_check_request, character
    ):
        fake = Faker()
        date = timezone.now()
        message = fake.text(100)
        with pytest.raises(PermissionDenied):
            process_roll.delay(
                game_id=fake.random_int(min=1000),
                roll_type=RollRequest.RollType.ABILITY_CHECK,
                date=date.isoformat(),
                character_id=character.id,
                message=message,
            ).get()

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollRequest.Status.PENDING

    def test_roll_failure_character_not_found(
        self, celery_worker, ability_check_request, game
    ):
        fake = Faker()
        date = timezone.now()
        message = fake.text(100)
        with pytest.raises(PermissionDenied):
            process_roll.delay(
                game_id=game.id,
                roll_type=RollRequest.RollType.ABILITY_CHECK,
                date=date.isoformat(),
                character_id=fake.random_int(min=1000),
                message=message,
            ).get()

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollRequest.Status.PENDING

    def test_roll_failure_request_not_found(
        self, celery_worker, ability_check_request, game, character
    ):
        fake = Faker()
        date = timezone.now()
        message = fake.text(100)
        RollRequest.objects.last().delete()
        with pytest.raises(PermissionDenied):
            process_roll.delay(
                game_id=game.id,
                roll_type=RollRequest.RollType.ABILITY_CHECK,
                date=date.isoformat(),
                character_id=character.id,
                message=message,
            ).get()

    @pytest.fixture
    def saving_throw_request(self):
        return RollRequestFactory(roll_type=RollRequest.RollType.SAVING_THROW)

    def test_saving_throw_success(
        self, celery_worker, saving_throw_request, game, character
    ):
        fake = Faker()
        date = timezone.now()
        message = fake.text(100)
        process_roll.delay(
            game_id=game.id,
            roll_type=RollRequest.RollType.SAVING_THROW,
            date=date.isoformat(),
            character_id=character.id,
            message=message,
        ).get()

        assert character.player.game == game

        roll = Roll.objects.last()
        assert roll.game == game
        assert (roll.date.second - date.second) <= 2
        # SequenceMatcher is used as the score is a random value, and therefore
        # cannot be guessed.
        expected_str = f"[{character.user}]'s score: 5, \
            {RollRequest.RollType.SAVING_THROW} result: {roll.get_result_display()}"
        s = SequenceMatcher(None, roll.message, expected_str)
        assert s.ratio() > 0.9

        saving_throw_request = RollRequest.objects.last()
        assert saving_throw_request.status == RollRequest.Status.DONE
