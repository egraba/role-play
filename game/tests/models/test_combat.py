import pytest
from ..factories import CombatFactory
from game.models.combat import Fighter

pytestmark = pytest.mark.django_db


class TestCombatModel:
    @pytest.fixture
    def combat(self):
        return CombatFactory()

    def test_get_initiative_order(self, combat):
        fighters = list(Fighter.objects.filter(combat=combat))
        assert combat.get_initiative_order() == fighters
