import pytest
from celery.exceptions import InvalidTaskError
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from faker import Faker

from game.constants.events import RollStatus, RollType
from game.models.combat import Combat, Fighter
from game.models.events import (
    CombatInitativeOrderSet,
    CombatInitialization,
    CombatInitiativeRequest,
    CombatInitiativeResponse,
    CombatInitiativeResult,
    Message,
    RollRequest,
    RollResponse,
    RollResult,
)
from game.tasks import (
    check_combat_roll_initiative_complete,
    process_combat_initiative_roll,
    process_roll,
    send_mail,
    store_message,
)

from .factories import (
    ActorFactory,
    CombatFactory,
    CombatInitalizationFactory,
    CombatInitiativeRequestFactory,
    FighterFactory,
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
    def test_message_message_stored_from_master(self, celery_session_worker):
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

    def test_message_message_stored_from_player(self, celery_session_worker):
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

    def test_message_message_stored_from_unfound_author(self, celery_session_worker):
        fake = Faker()
        game = GameFactory()
        with pytest.raises(InvalidTaskError):
            store_message.delay(
                game_id=game.id,
                author_str=fake.user_name(),
                date=timezone.now(),
                message=fake.text(100),
            ).get()

    def test_message_game_not_found(self, celery_session_worker):
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
        self, celery_session_worker, ability_check_request
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
        self, celery_session_worker, ability_check_request
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
        self, celery_session_worker, ability_check_request
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
        self, celery_session_worker, ability_check_request
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
        self, celery_session_worker, saving_throw_request
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
        self, celery_session_worker, combat_initiative_request
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
        self, celery_session_worker, combat_initiative_request
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
        self, celery_session_worker, combat_initiative_request
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
        self, celery_session_worker, combat_initiative_request
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


class TestCheckCombatRollInitiativeComplete:
    """Tests for the check_combat_roll_initiative_complete task."""

    def test_no_combat_exists(self, mocker):
        """Test that task handles case when no combat exists."""
        # Ensure no combats exist
        Combat.objects.all().delete()
        mock_send = mocker.patch("game.tasks.send_to_channel")

        # Should execute without error when no combat exists
        check_combat_roll_initiative_complete()

        # No channel message should be sent
        mock_send.assert_not_called()

    def test_combat_with_pending_initiative_roll(self, mocker):
        """Test that task waits when some fighters haven't rolled yet."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)

        # Create player and character
        player1 = PlayerFactory(game=game)
        player2 = PlayerFactory(game=game)

        # Create fighters - one has rolled, one hasn't
        Fighter.objects.create(
            player=player1,
            character=player1.character,
            combat=combat,
            dexterity_check=15,  # Has rolled
        )
        Fighter.objects.create(
            player=player2,
            character=player2.character,
            combat=combat,
            dexterity_check=None,  # Hasn't rolled yet
        )

        # Create the CombatInitialization event
        author = game.master.actor_ptr
        CombatInitialization.objects.create(game=game, author=author, combat=combat)

        mock_send = mocker.patch("game.tasks.send_to_channel")

        check_combat_roll_initiative_complete()

        # No channel message should be sent since we're still waiting
        mock_send.assert_not_called()

    def test_combat_all_initiative_rolls_complete(self, mocker, db):
        """Test that task sends initiative order when all fighters have rolled."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)

        # Create players and fighters - all have rolled
        player1 = PlayerFactory(game=game)
        player2 = PlayerFactory(game=game)

        Fighter.objects.create(
            player=player1,
            character=player1.character,
            combat=combat,
            dexterity_check=18,
        )
        Fighter.objects.create(
            player=player2,
            character=player2.character,
            combat=combat,
            dexterity_check=12,
        )

        # Create the CombatInitialization event
        author = game.master.actor_ptr
        CombatInitialization.objects.create(game=game, author=author, combat=combat)

        # Create a periodic task for this game
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=2,
            period=IntervalSchedule.SECONDS,
        )
        periodic_task = PeriodicTask.objects.create(
            interval=schedule,
            name=f"game{game.id}: Check if combat roll initiative is complete",
            task="game.tasks.check_combat_roll_initiative_complete",
            enabled=True,
        )

        mock_send = mocker.patch("game.tasks.send_to_channel")

        check_combat_roll_initiative_complete()

        # Verify CombatInitativeOrderSet was created
        assert CombatInitativeOrderSet.objects.filter(combat=combat).exists()
        order_set = CombatInitativeOrderSet.objects.get(combat=combat)
        assert order_set.game == game
        assert order_set.author == author

        # Verify channel message was sent
        mock_send.assert_called_once()

        # Verify periodic task was disabled
        periodic_task.refresh_from_db()
        assert periodic_task.enabled is False

    def test_combat_initiative_order_set_already_exists(self, mocker, db):
        """Test that task doesn't create duplicate order set."""
        game = GameFactory()
        combat = Combat.objects.create(game=game)

        # Create player and fighter
        player = PlayerFactory(game=game)
        Fighter.objects.create(
            player=player,
            character=player.character,
            combat=combat,
            dexterity_check=15,
        )

        # Create the CombatInitialization event
        author = game.master.actor_ptr
        CombatInitialization.objects.create(game=game, author=author, combat=combat)

        # Create existing order set
        CombatInitativeOrderSet.objects.create(game=game, author=author, combat=combat)

        # Create periodic task
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=2,
            period=IntervalSchedule.SECONDS,
        )
        PeriodicTask.objects.create(
            interval=schedule,
            name=f"game{game.id}: Check if combat roll initiative is complete",
            task="game.tasks.check_combat_roll_initiative_complete",
            enabled=True,
        )

        mock_send = mocker.patch("game.tasks.send_to_channel")

        check_combat_roll_initiative_complete()

        # No new order set should be created (still just 1)
        assert CombatInitativeOrderSet.objects.filter(combat=combat).count() == 1

        # No channel message should be sent since order set already existed
        mock_send.assert_not_called()
