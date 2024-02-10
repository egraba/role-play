from django.utils import timezone

from game.models.events import RollRequest
from game.tasks import process_roll


class TestProcessRoll:
    def test_ability_check(self, celery_worker):
        process_roll.delay(
            game_id=None,
            roll_type=RollRequest.RollType.ABILITY_CHECK,
            date=timezone.now().isoformat(),
            character_id=None,
            message=None,
        )
