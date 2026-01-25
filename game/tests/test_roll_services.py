import pytest
from django.utils import timezone

from game.constants.events import RollStatus, RollType
from game.models.events import (
    CombatInitiativeRequest,
    CombatInitiativeResponse,
    CombatInitiativeResult,
    RollRequest,
    RollResponse,
    RollResult,
)
from game.services import GameEventService

from .factories import (
    CombatInitalizationFactory,
    CombatInitiativeRequestFactory,
    RollRequestFactory,
)

pytestmark = pytest.mark.django_db(transaction=True)


class TestProcessRoll:
    @pytest.fixture
    def ability_check_request(self):
        return RollRequestFactory(roll_type=RollType.ABILITY_CHECK)

    def test_process_roll_ability_check_success(self, ability_check_request):
        game = ability_check_request.game
        player = ability_check_request.player
        date = timezone.now()
        GameEventService.process_roll(
            game=game,
            player=player,
            date=date,
            roll_type=RollType.ABILITY_CHECK,
        )

        assert player.game == game

        roll_response = RollResponse.objects.last()
        assert roll_response.game == game

        roll_result = RollResult.objects.last()
        assert roll_result.game == game

        ability_check_request = RollRequest.objects.last()
        assert ability_check_request.status == RollStatus.DONE

    def test_process_roll_failure_request_not_found(self, ability_check_request):
        game = ability_check_request.game
        player = ability_check_request.player
        date = timezone.now()
        RollRequest.objects.last().delete()
        with pytest.raises(RollRequest.DoesNotExist):
            GameEventService.process_roll(
                game=game,
                player=player,
                date=date,
                roll_type=RollType.ABILITY_CHECK,
            )

    @pytest.fixture
    def saving_throw_request(self):
        return RollRequestFactory(roll_type=RollType.SAVING_THROW)

    def test_process_roll_saving_throw_success(self, saving_throw_request):
        game = saving_throw_request.game
        player = saving_throw_request.player
        date = timezone.now()
        GameEventService.process_roll(
            game=game,
            player=player,
            date=date,
            roll_type=RollType.SAVING_THROW,
        )

        assert player.game == game

        roll_result = RollResult.objects.last()
        assert roll_result.game == game

        saving_throw_request = RollRequest.objects.last()
        assert saving_throw_request.status == RollStatus.DONE


class TestProcessCombatInitiativeRoll:
    @pytest.fixture
    def combat_initiative_request(self):
        request = CombatInitiativeRequestFactory()
        # Create the CombatInitialization event required by _check_and_start_combat
        CombatInitalizationFactory(
            game=request.game,
            combat=request.fighter.combat,
            author=request.game.master.actor_ptr,
        )
        return request

    def test_process_combat_initiative_roll_success(self, combat_initiative_request):
        game = combat_initiative_request.game
        player = combat_initiative_request.fighter.player
        date = timezone.now()
        GameEventService.process_combat_initiative_roll(
            game=game,
            player=player,
            date=date,
        )

        roll_response = CombatInitiativeResponse.objects.last()
        assert roll_response.game == game

        roll_result = CombatInitiativeResult.objects.last()
        assert roll_result.game == game

        combat_initiative_request = CombatInitiativeRequest.objects.last()
        assert combat_initiative_request.status == RollStatus.DONE

    def test_process_combat_initiative_roll_failure_request_not_found(
        self, combat_initiative_request
    ):
        game = combat_initiative_request.fighter.character.player.game
        player = combat_initiative_request.fighter.player
        date = timezone.now()
        CombatInitiativeRequest.objects.last().delete()
        with pytest.raises(CombatInitiativeRequest.DoesNotExist):
            GameEventService.process_combat_initiative_roll(
                game=game,
                player=player,
                date=date,
            )
