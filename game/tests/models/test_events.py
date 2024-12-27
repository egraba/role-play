import pytest
from django.utils import timezone
from freezegun import freeze_time

from game.models.events import (
    UserInvitation,
    CombatInitialization,
    Event,
    GameStart,
    Message,
    QuestUpdate,
    RollRequest,
    RollResponse,
    RollResult,
)
from utils.constants import FREEZED_TIME

from ..factories import (
    UserInvitationFactory,
    CombatInitalizationFactory,
    EventFactory,
    GameStartFactory,
    MessageFactory,
    PlayerFactory,
    QuestUpdateFactory,
    RollRequestFactory,
    RollResponseFactory,
    RollResultFactory,
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
        return MessageFactory(is_from_master=True)

    def test_get_message_from_master(self, message_from_master):
        assert (
            message_from_master.get_message()
            == f"The Master said: {message_from_master.content}"
        )

    @pytest.fixture
    def message_from_player(self):
        return MessageFactory(is_from_master=False, author=PlayerFactory())

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
            == f"{roll_request.character} needs to perform a {roll_request.ability_type} check! \
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
            == f"{roll_response.character} performed an ability check!"
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
            == f"[{roll_result.character.user}]'s score: {roll_result.score}, \
            {roll_result.request.roll_type} result: {roll_result.get_result_display()}"
        )


class TestCombatInitializationModel:
    @pytest.fixture
    def combat_init(self):
        return CombatInitalizationFactory()

    def test_creation(self, combat_init):
        assert isinstance(combat_init, CombatInitialization)

    def test_get_message(self, combat_init):
        assert combat_init.get_message().startswith("Combat!")
