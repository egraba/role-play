import random

import pytest
from django.utils import timezone

from game.models.events import Damage, DiceLaunch, Event, Healing, Quest, XpIncrease

from ..factories import EventFactory, GameFactory, PlayerFactory


@pytest.mark.django_db
class TestEventModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.event = EventFactory()

    def test_creation(self):
        assert isinstance(self.event, Event)
        assert self.event.date.second - timezone.now().second <= 2

    def test_str(self):
        assert str(self.event) == self.event.message


@pytest.mark.django_db
class TestQuestModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        game = GameFactory()
        self.quest = Quest.objects.filter(game=game).last()

    def test_creation(self):
        assert isinstance(self.quest, Quest)

    def test_str(self):
        assert str(self.quest) == self.quest.content


@pytest.mark.django_db
class TestXpIncreaseModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        self.xp_increase = XpIncrease.objects.create(
            game=game, character=player.character, xp=random.randint(1, 20)
        )

    def test_creation(self):
        assert isinstance(self.xp_increase, XpIncrease)

    def test_str(self):
        assert str(self.xp_increase) == str(self.xp_increase.xp)


@pytest.mark.django_db
class TestDamageModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        self.damage = Damage.objects.create(
            game=game, character=player.character, hp=random.randint(1, 20)
        )

    def test_creation(self):
        assert isinstance(self.damage, Damage)

    def test_str(self):
        assert str(self.damage) == str(self.damage.hp)


@pytest.mark.django_db
class TestHealingModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        self.healing = Healing.objects.create(
            game=game, character=player.character, hp=random.randint(1, 20)
        )

    def test_creation(self):
        assert isinstance(self.healing, Healing)

    def test_str(self):
        assert str(self.healing) == str(self.healing.hp)


@pytest.mark.django_db
class TestDiceLaunchModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        game = GameFactory()
        player = PlayerFactory(game=game)
        self.dice_launch = DiceLaunch.objects.create(
            game=game, character=player.character, score=random.randint(1, 20)
        )

    def test_creation(self):
        assert isinstance(self.dice_launch, DiceLaunch)

    def test_str(self):
        assert str(self.dice_launch) == str(self.dice_launch.score)
