import pytest
from celery.exceptions import InvalidTaskError
from django.utils import timezone
from faker import Faker

from game.constants.events import RollStatus, RollType
from game.models.events import Message, RollRequest, RollResponse, RollResult
from game.models.game import Game, Player
from game.tasks import process_roll, store_message

from .factories import GameFactory, MessageFactory, RollRequestFactory

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture(scope="session")
def celery_parameters():
    # Used to suppress warnings during test sessions.
    return {"broker_connection_retry_on_startup": True}


class TestStoreMessage:
    @pytest.fixture
    def game(self):
        return GameFactory()

    @pytest.fixture
    def message(self):
        return MessageFactory()

    def test_message_message_stored(self, celery_worker, game):
        fake = Faker()
        date = timezone.now()
        message = fake.text(100)
        store_message.delay(
            game_id=game.id,
            date=date,
            message=message,
            is_from_master=fake.boolean(),
            author_name=None,
        ).get()
        message = Message.objects.last()
        assert message.game == game
        assert message.message == message

    def test_message_game_not_found(self, celery_worker):
        fake = Faker()
        with pytest.raises(InvalidTaskError):
            store_message.delay(
                game_id=fake.random_int(min=9999),
                date=timezone.now(),
                message=fake.text(100),
                is_from_master=fake.boolean(),
                author_name=None,
            ).get()


class TestProcessRoll:
    @pytest.fixture
    def game(self):
        # Retrieved from RollRequestFactory.
        return Game.objects.last()

    @pytest.fixture
    def player(self):
        # Retrieved from RollRequestFactory.
        return Player.objects.last()

    @pytest.fixture
    def ability_check_request(self):
        return RollRequestFactory(roll_type=RollType.ABILITY_CHECK)

    def test_process_roll_ability_check_success(
        self, celery_worker, ability_check_request, game, player
    ):
        date = timezone.now()
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.ABILITY_CHECK,
            date=date,
            player_id=player.id,
        ).get()

        assert player.game == game

        roll_response = RollResponse.objects.last()
        assert roll_response.game == game

        roll_result = RollResult.objects.last()
        assert roll_result.game == game

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollStatus.DONE

    def test_process_roll_failure_game_not_found(
        self, celery_worker, ability_check_request, player
    ):
        fake = Faker()
        date = timezone.now()
        with pytest.raises(InvalidTaskError):
            process_roll.delay(
                game_id=fake.random_int(min=1000),
                roll_type=RollType.ABILITY_CHECK,
                date=date.isoformat(),
                player_id=player.id,
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
                player_id=fake.random_int(min=1000),
            ).get()

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollStatus.PENDING

    def test_process_roll_failure_request_not_found(
        self, celery_worker, ability_check_request, game, player
    ):
        date = timezone.now()
        RollRequest.objects.last().delete()
        with pytest.raises(InvalidTaskError):
            process_roll.delay(
                game_id=game.id,
                roll_type=RollType.ABILITY_CHECK,
                date=date.isoformat(),
                player_id=player.id,
            ).get()

    @pytest.fixture
    def saving_throw_request(self):
        return RollRequestFactory(roll_type=RollType.SAVING_THROW)

    def test_process_roll_saving_throw_success(
        self, celery_worker, saving_throw_request, game, player
    ):
        date = timezone.now()
        process_roll.delay(
            game_id=game.id,
            roll_type=RollType.SAVING_THROW,
            date=date.isoformat(),
            player_id=player.id,
        ).get()

        assert player.game == game

        roll_result = RollResult.objects.last()
        assert roll_result.game == game

        saving_throw_request = RollRequest.objects.last()
        assert saving_throw_request.status == RollStatus.DONE
