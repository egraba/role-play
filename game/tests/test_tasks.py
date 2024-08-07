import pytest
from celery.exceptions import InvalidTaskError
from django.utils import timezone
from faker import Faker

from character.models.character import Character
from game.constants.events import RollStatus, RollType
from game.models.events import RollRequest, RollResult, RollResponse
from game.models.game import Game
from game.tasks import process_roll

from .factories import RollRequestFactory


@pytest.fixture(scope="session")
def celery_parameters():
    # Used to suppress warnings during test sessions.
    return {"broker_connection_retry_on_startup": True}


@pytest.mark.django_db(transaction=True)
class TestProcessRoll:
    @pytest.fixture
    def ability_check_request(self):
        return RollRequestFactory(roll_type=RollType.ABILITY_CHECK)

    @pytest.fixture
    def game(self):
        # Retrieved from RollRequestFactory.
        return Game.objects.last()

    @pytest.fixture
    def character(self):
        # Retrieved from RollRequestFactory.
        return Character.objects.last()

    def test_process_roll_ability_check_success(
        self, celery_worker, ability_check_request, game, character
    ):
        date = timezone.now()
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.ABILITY_CHECK,
            date=date,
            character_id=character.id,
        ).get()

        assert character.player.game == game

        roll_response = RollResponse.objects.last()
        assert roll_response.game == game
        assert (roll_response.date.second - date.second) <= 2

        roll_result = RollResult.objects.last()
        assert roll_result.game == game
        assert (roll_result.date.second - date.second) <= 2

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollStatus.DONE

    def test_process_roll_failure_game_not_found(
        self, celery_worker, ability_check_request, character
    ):
        fake = Faker()
        date = timezone.now()
        with pytest.raises(InvalidTaskError):
            process_roll.delay(
                game_id=fake.random_int(min=1000),
                roll_type=RollType.ABILITY_CHECK,
                date=date.isoformat(),
                character_id=character.id,
            ).get()

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollStatus.PENDING

    def test_process_roll_failure_character_not_found(
        self, celery_worker, ability_check_request, game
    ):
        fake = Faker()
        date = timezone.now()
        with pytest.raises(InvalidTaskError):
            process_roll.delay(
                game_id=game.id,
                roll_type=RollType.ABILITY_CHECK,
                date=date.isoformat(),
                character_id=fake.random_int(min=1000),
            ).get()

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollStatus.PENDING

    def test_process_roll_failure_request_not_found(
        self, celery_worker, ability_check_request, game, character
    ):
        date = timezone.now()
        RollRequest.objects.last().delete()
        with pytest.raises(InvalidTaskError):
            process_roll.delay(
                game_id=game.id,
                roll_type=RollType.ABILITY_CHECK,
                date=date.isoformat(),
                character_id=character.id,
            ).get()

    @pytest.fixture
    def saving_throw_request(self):
        return RollRequestFactory(roll_type=RollType.SAVING_THROW)

    def test_process_roll_saving_throw_success(
        self, celery_worker, saving_throw_request, game, character
    ):
        date = timezone.now()
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.SAVING_THROW,
            date=date.isoformat(),
            character_id=character.id,
        ).get()

        assert character.player.game == game

        roll_result = RollResult.objects.last()
        assert roll_result.game == game
        assert (roll_result.date.second - date.second) <= 2

        saving_throw_request = RollRequest.objects.last()
        assert saving_throw_request.status == RollStatus.DONE
