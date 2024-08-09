import pytest
from django.utils import timezone

from game.models.events import (
    CharacterInvitation,
    CombatInitialization,
    Event,
    GameStart,
    Message,
    QuestUpdate,
    RollRequest,
    RollResponse,
    RollResult,
)

from ..factories import (
    CharacterInvitationFactory,
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
    @pytest.fixture
    def event(self):
        return EventFactory()

    def test_creation(self, event):
        assert isinstance(event, Event)
        assert event.date.second - timezone.now().second <= 2


class TestGameStartModel:
    @pytest.fixture
    def game_start(self):
        return GameStartFactory()

    def test_creation(self, game_start):
        assert isinstance(game_start, GameStart)

    def test_get_message(self, game_start):
        assert game_start.get_message() == "The game started."


class TestCharacterInvitationModel:
    @pytest.fixture
    def character_invitation(self):
        return CharacterInvitationFactory()

    def test_creation(self, character_invitation):
        assert isinstance(character_invitation, CharacterInvitation)

    def test_get_message(self, character_invitation):
        assert (
            character_invitation.get_message()
            == f"{character_invitation.character} was added to the game."
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


class TestCharacterInvitationModel:
    @pytest.fixture
    def character_invitation(self):
        return CharacterInvitationFactory()

    def test_creation(self, character_invitation):
        assert isinstance(character_invitation, CharacterInvitation)

    def test_get_message(self, character_invitation):
        assert (
            character_invitation.get_message()
            == f"{character_invitation.character} was added to the game."
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
    def quest(self):
        return QuestUpdateFactory()

    def test_creation(self, quest):
        assert isinstance(quest, QuestUpdate)

    def test_str(self, quest):
        assert str(quest) == quest.content[:10]

    def test_get_message(self, quest):
        assert quest.get_message() == "The Master updated the quest."


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
