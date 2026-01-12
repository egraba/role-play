import pytest
from django.utils import timezone
from freezegun import freeze_time

from game.models.events import (
    CombatEnded,
    CombatInitialization,
    CombatStarted,
    Event,
    GameStart,
    Message,
    QuestUpdate,
    RollRequest,
    RollResponse,
    RollResult,
    RoundEnded,
    TurnEnded,
    TurnStarted,
    UserInvitation,
)
from utils.constants import FREEZED_TIME

from ..factories import (
    ActorFactory,
    CombatEndedFactory,
    CombatInitalizationFactory,
    CombatStartedFactory,
    EventFactory,
    FighterFactory,
    GameFactory,
    GameStartFactory,
    MessageFactory,
    PlayerFactory,
    QuestUpdateFactory,
    RollRequestFactory,
    RollResponseFactory,
    RollResultFactory,
    RoundEndedFactory,
    TurnEndedFactory,
    TurnStartedFactory,
    UserInvitationFactory,
)

pytestmark = pytest.mark.django_db


class TestEventModel:
    @freeze_time(FREEZED_TIME)
    def test_creation(self):
        event = EventFactory()
        assert isinstance(event, Event)
        assert event.date == timezone.now()


class TestGameStartModel:
    @pytest.fixture
    def game_start(self):
        return GameStartFactory()

    def test_creation(self, game_start):
        assert isinstance(game_start, GameStart)

    def test_get_message(self, game_start):
        assert game_start.get_message() == "The game started."


class TestUserInvitationModel:
    @pytest.fixture
    def user_invitation(self):
        return UserInvitationFactory()

    def test_creation(self, user_invitation):
        assert isinstance(user_invitation, UserInvitation)

    def test_get_message(self, user_invitation):
        assert (
            user_invitation.get_message()
            == f"{user_invitation.user} was added to the game."
        )


class TestMessageModel:
    @pytest.fixture
    def message(self):
        return MessageFactory()

    def test_creation(self, message):
        assert isinstance(message, Message)

    @pytest.fixture
    def message_from_master(self):
        game = GameFactory()
        author = ActorFactory()
        author.master = game.master
        return MessageFactory(game=game, author=author)

    def test_get_message_from_master(self, message_from_master):
        assert (
            message_from_master.get_message()
            == f"The Master said: {message_from_master.content}"
        )

    @pytest.fixture
    def message_from_player(self):
        game = GameFactory()
        author = ActorFactory()
        player = PlayerFactory(game=game)
        author.player = player
        return MessageFactory(game=game, author=author)

    def test_get_message_from_player(self, message_from_player):
        assert (
            message_from_player.get_message()
            == f"{message_from_player.author} said: {message_from_player.content}"
        )


class TestQuestUpdateModel:
    @pytest.fixture
    def quest_update(self):
        return QuestUpdateFactory()

    def test_creation(self, quest_update):
        assert isinstance(quest_update, QuestUpdate)

    def test_str(self, quest_update):
        assert str(quest_update) == quest_update.quest.environment[:10]

    def test_get_message(self, quest_update):
        assert quest_update.get_message() == "The Master updated the quest."


class TestRollRequestModel:
    @pytest.fixture
    def roll_request(self):
        return RollRequestFactory()

    def test_creation(self, roll_request):
        assert isinstance(roll_request, RollRequest)

    def test_get_message(self, roll_request):
        assert (
            roll_request.get_message()
            == f"{roll_request.player} needs to perform a {roll_request.ability_type} check! \
            Difficulty: {roll_request.get_difficulty_class_display()}."
        )


class TestRollResponseModel:
    @pytest.fixture
    def roll_response(self):
        return RollResponseFactory(request=RollRequestFactory())

    def test_creation(self, roll_response):
        assert isinstance(roll_response, RollResponse)

    def test_get_message(self, roll_response):
        assert (
            roll_response.get_message()
            == f"{roll_response.request.player} performed an ability check!"
        )


class TestRollResultModel:
    @pytest.fixture
    def roll_result(self):
        roll_request = RollRequestFactory()
        roll_response = RollResponseFactory(request=roll_request)
        return RollResultFactory(request=roll_request, response=roll_response)

    def test_creation(self, roll_result):
        assert isinstance(roll_result, RollResult)

    def test_get_message(self, roll_result):
        assert (
            roll_result.get_message()
            == f"{roll_result.request.player}'s score: {roll_result.score}, \
            {roll_result.request.get_roll_type_display()} result: {roll_result.get_result_display()}"
        )


class TestCombatInitializationModel:
    @pytest.fixture
    def combat_init(self):
        return CombatInitalizationFactory()

    def test_creation(self, combat_init):
        assert isinstance(combat_init, CombatInitialization)

    def test_get_message(self, combat_init):
        assert combat_init.get_message().startswith("Combat!")

    def test_get_message_single_fighter_no_initiative_order_prefix(self, combat_init):
        # Remove all fighters and add just one
        combat_init.combat.fighter_set.all().delete()
        FighterFactory(combat=combat_init.combat, dexterity_check=10)
        message = combat_init.get_message()
        assert message.startswith("Combat!")
        assert "Initiative order:" not in message

    def test_get_message_multiple_fighters_has_initiative_order_prefix(
        self, combat_init
    ):
        # Ensure there are at least 2 fighters
        combat_init.combat.fighter_set.all().delete()
        FighterFactory(combat=combat_init.combat, dexterity_check=10)
        FighterFactory(combat=combat_init.combat, dexterity_check=15)
        message = combat_init.get_message()
        assert message.startswith("Combat! Initiative order:")


class TestCombatStartedModel:
    @pytest.fixture
    def combat_started(self):
        return CombatStartedFactory()

    def test_creation(self, combat_started):
        assert isinstance(combat_started, CombatStarted)

    def test_get_message(self, combat_started):
        assert (
            combat_started.get_message()
            == "Combat has begun! Roll for initiative order has been determined."
        )


class TestTurnStartedModel:
    @pytest.fixture
    def turn_started(self):
        return TurnStartedFactory()

    def test_creation(self, turn_started):
        assert isinstance(turn_started, TurnStarted)

    def test_get_message(self, turn_started):
        expected = f"Round {turn_started.round_number}: {turn_started.fighter.character.name}'s turn!"
        assert turn_started.get_message() == expected


class TestTurnEndedModel:
    @pytest.fixture
    def turn_ended(self):
        return TurnEndedFactory()

    def test_creation(self, turn_ended):
        assert isinstance(turn_ended, TurnEnded)

    def test_get_message(self, turn_ended):
        expected = f"{turn_ended.fighter.character.name}'s turn has ended."
        assert turn_ended.get_message() == expected


class TestRoundEndedModel:
    @pytest.fixture
    def round_ended(self):
        return RoundEndedFactory()

    def test_creation(self, round_ended):
        assert isinstance(round_ended, RoundEnded)

    def test_get_message(self, round_ended):
        expected = f"Round {round_ended.round_number} has ended."
        assert round_ended.get_message() == expected


class TestCombatEndedModel:
    @pytest.fixture
    def combat_ended(self):
        return CombatEndedFactory()

    def test_creation(self, combat_ended):
        assert isinstance(combat_ended, CombatEnded)

    def test_get_message(self, combat_ended):
        assert combat_ended.get_message() == "Combat has ended."
