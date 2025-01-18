import pytest
from celery.exceptions import InvalidTaskError
from django.utils import timezone
from faker import Faker

from game.constants.events import RollStatus, RollType
from game.models.events import (
    CombatInitiativeRequest,
    CombatInitiativeResponse,
    CombatInitiativeResult,
    Message,
    RollRequest,
    RollResponse,
    RollResult,
)
from game.tasks import (
    process_combat_initiative_roll,
    process_roll,
    send_mail,
    store_message,
)

from .factories import (
    CombatInitiativeRequestFactory,
    GameFactory,
    PlayerFactory,
    RollRequestFactory,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture(scope="session")
def celery_parameters():
    # Used to suppress warnings during test sessions.
    return {"broker_connection_retry_on_startup": True}


class TestSendMail:
    def test_send_mail(self, mocker):
        fake = Faker()
        subject = fake.sentence()
        message = fake.text()
        from_email = fake.email()
        recipient_list = [fake.email() for _ in range(3)]
        mocked_send_mail = mocker.patch("game.tasks.django_send_mail")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
        )
        mocked_send_mail.assert_called_once_with(
            subject, message, from_email, recipient_list
        )


class TestStoreMessage:
    def test_message_message_stored_from_master(self, celery_worker):
        fake = Faker()
        game = GameFactory()
        store_message.delay(
            game_id=game.id,
            author_str=game.master.user.username,
            date=timezone.now(),
            message=fake.text(100),
        ).get()
        message = Message.objects.last()
        assert message.game == game
        assert message.author == game.master.actor_ptr
        assert message.message == message

    def test_message_message_stored_from_player(self, celery_worker):
        fake = Faker()
        game = GameFactory()
        player = PlayerFactory(game=game)
        store_message.delay(
            game_id=game.id,
            author_str=player.user.username,
            date=timezone.now(),
            message=fake.text(100),
        ).get()
        message = Message.objects.last()
        assert message.game == game
        assert message.author == player.actor_ptr
        assert message.message == message

    def test_message_message_stored_from_unfound_author(self, celery_worker):
        fake = Faker()
        game = GameFactory()
        with pytest.raises(InvalidTaskError):
            store_message.delay(
                game_id=game.id,
                author_str=fake.user_name(),
                date=timezone.now(),
                message=fake.text(100),
            ).get()

    def test_message_game_not_found(self, celery_worker):
        fake = Faker()
        with pytest.raises(InvalidTaskError):
            store_message.delay(
                game_id=fake.random_int(min=9999),
                date=timezone.now(),
                message=fake.text(100),
                author_str=fake.user_name(),
            ).get()


class TestProcessRoll:
    @pytest.fixture
    def ability_check_request(self):
        return RollRequestFactory(roll_type=RollType.ABILITY_CHECK)

    def test_process_roll_ability_check_success(
        self, celery_worker, ability_check_request
    ):
        game = ability_check_request.game
        player = ability_check_request.player
        date = timezone.now()
        process_roll.delay(
            game_id=game.id,
            author_id=player.actor_ptr.id,
            date=date,
            roll_type=RollType.ABILITY_CHECK,
        ).get()

        assert player.game == game

        roll_response = RollResponse.objects.last()
        assert roll_response.game == game

        roll_result = RollResult.objects.last()
        assert roll_result.game == game

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollStatus.DONE

    def test_process_roll_failure_game_not_found(
        self, celery_worker, ability_check_request
    ):
        fake = Faker()
        player = ability_check_request.player
        date = timezone.now()
        with pytest.raises(InvalidTaskError):
            process_roll.delay(
                game_id=fake.random_int(min=1000),
                author_id=player.actor_ptr.id,
                roll_type=RollType.ABILITY_CHECK,
                date=date.isoformat(),
            ).get()

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollStatus.PENDING

    def test_process_roll_failure_author_not_found(
        self, celery_worker, ability_check_request
    ):
        fake = Faker()
        game = ability_check_request.game
        date = timezone.now()
        with pytest.raises(InvalidTaskError):
            process_roll.delay(
                game_id=game.id,
                author_id=fake.random_int(min=1000),
                roll_type=RollType.ABILITY_CHECK,
                date=date.isoformat(),
            ).get()

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollStatus.PENDING

    def test_process_roll_failure_request_not_found(
        self, celery_worker, ability_check_request
    ):
        game = ability_check_request.game
        player = ability_check_request.player
        date = timezone.now()
        RollRequest.objects.last().delete()
        with pytest.raises(InvalidTaskError):
            process_roll.delay(
                game_id=game.id,
                author_id=player.actor_ptr.id,
                roll_type=RollType.ABILITY_CHECK,
                date=date.isoformat(),
            ).get()

    @pytest.fixture
    def saving_throw_request(self):
        return RollRequestFactory(roll_type=RollType.SAVING_THROW)

    def test_process_roll_saving_throw_success(
        self, celery_worker, saving_throw_request
    ):
        game = saving_throw_request.game
        player = saving_throw_request.player
        date = timezone.now()
        process_roll.delay(
            game_id=game.id,
            author_id=player.actor_ptr.id,
            roll_type=RollType.SAVING_THROW,
            date=date.isoformat(),
        ).get()

        assert player.game == game

        roll_result = RollResult.objects.last()
        assert roll_result.game == game

        saving_throw_request = RollRequest.objects.last()
        assert saving_throw_request.status == RollStatus.DONE


class TestProcessCombatInitiativeRoll:
    @pytest.fixture
    def combat_initiative_request(self):
        return CombatInitiativeRequestFactory()

    def test_process_combat_initiative_roll_success(
        self, celery_worker, combat_initiative_request
    ):
        game = combat_initiative_request.game
        player = combat_initiative_request.fighter.player
        date = timezone.now()
        process_combat_initiative_roll.delay(
            game_id=game.id,
            player_id=player.id,
            date=date,
        ).get()

        roll_response = CombatInitiativeResponse.objects.last()
        assert roll_response.game == game

        roll_result = CombatInitiativeResult.objects.last()
        assert roll_result.game == game

        combat_initiative_request = CombatInitiativeRequest.objects.last()
        assert combat_initiative_request.status == RollStatus.DONE

    def test_process_combat_initiative_roll_failure_game_not_found(
        self, celery_worker, combat_initiative_request
    ):
        fake = Faker()
        player = combat_initiative_request.fighter.player
        date = timezone.now()
        with pytest.raises(InvalidTaskError):
            process_combat_initiative_roll.delay(
                game_id=fake.random_int(min=1000),
                player_id=player.id,
                date=date.isoformat(),
            ).get()

        combat_initiative_request = CombatInitiativeRequest.objects.last()
        assert combat_initiative_request.status == RollStatus.PENDING

    def test_process_combat_initiative_roll_failure_player_not_found(
        self, celery_worker, combat_initiative_request
    ):
        fake = Faker()
        game = combat_initiative_request.game
        date = timezone.now()
        with pytest.raises(InvalidTaskError):
            process_combat_initiative_roll.delay(
                game_id=game.id,
                player_id=fake.random_int(min=1000),
                date=date.isoformat(),
            ).get()

        combat_initiative_request = CombatInitiativeRequest.objects.last()
        assert combat_initiative_request.status == RollStatus.PENDING

    def test_process_combat_initiative_roll_failure_request_not_found(
        self, celery_worker, combat_initiative_request
    ):
        game = combat_initiative_request.fighter.character.player.game
        player = combat_initiative_request.fighter.player
        date = timezone.now()
        CombatInitiativeRequest.objects.last().delete()
        with pytest.raises(InvalidTaskError):
            process_combat_initiative_roll.delay(
                game_id=game.id,
                player_id=player.id,
                date=date.isoformat(),
            ).get()
