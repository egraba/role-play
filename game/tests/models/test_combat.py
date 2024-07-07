import pytest
from ..factories import CombatFactory

pytestmark = pytest.mark.django_db


class TestCombatModel:
    @pytest.fixture
    def combat(self):
        return CombatFactory()

    def test_get_initiative_order(self, combat):
        pass
