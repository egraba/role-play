from abc import abstractmethod

from django.conf import settings
from django.db import models
from model_utils.managers import InheritanceManager

from character.constants.abilities import AbilityName

from ..constants.events import (
    Against,
    DifficultyClass,
    RollResultType,
    RollStatus,
    RollType,
)
from ..exceptions import UnsupportedActor
from .combat import Combat, Fighter
from .game import Actor, Game, Player, Quest


class Event(models.Model):
    """
    Events are everything that occur in a game.

    This class shall not be instantiated explicitly.
    """

    objects = InheritanceManager()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    author = models.ForeignKey(Actor, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["-date"]),
        ]

    @abstractmethod
    def get_message(self):
        """
        Retrieve messages of an event.

        Messages represent "logs" of an event.
        Messages are not stored in database, only event content is.
        """
        pass


class GameStart(Event):
    def get_message(self):
        return "The game started."


class UserInvitation(Event):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_message(self):
        return f"{self.user} was added to the game."


class Message(Event):
    content = models.CharField(max_length=100)

    def __str__(self):
        return self.content

    def get_message(self):
        if hasattr(self.author, "master"):
            author_str = "The Master"
        elif hasattr(self.author, "player"):
            author_str = str(self.author)
        else:
            raise UnsupportedActor(f"{type(self.author)} is not supported")
        return f"{author_str} said: {self.content}"


class QuestUpdate(Event):
    quest = models.OneToOneField(Quest, on_delete=models.CASCADE)

    def __str__(self):
        return self.quest.environment[:10]

    def get_message(self):
        return "The Master updated the quest."


class RollRequest(Event):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=RollStatus, default=RollStatus.PENDING
    )
    ability_type = models.CharField(
        max_length=3,
        choices=AbilityName,
    )
    difficulty_class = models.SmallIntegerField(
        choices=DifficultyClass,
        blank=True,
        null=True,
    )
    roll_type = models.SmallIntegerField(choices=RollType)
    against = models.CharField(max_length=1, choices=Against, blank=True, null=True)
    is_combat = models.BooleanField(default=False)

    def get_message(self):
        return f"{self.player} needs to perform a {self.ability_type} check! \
            Difficulty: {self.get_difficulty_class_display()}."


class RollResponse(Event):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    request = models.ForeignKey(RollRequest, on_delete=models.CASCADE)

    def get_message(self):
        return f"{self.player} performed an ability check!"


class RollResult(Event):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    request = models.ForeignKey(RollRequest, on_delete=models.CASCADE)
    response = models.ForeignKey(RollResponse, on_delete=models.CASCADE)
    score = models.SmallIntegerField()
    result = models.CharField(max_length=1, choices=RollResultType)

    def get_message(self):
        return f"[{self.player.user}]'s score: {self.score}, \
            {self.request.roll_type} result: {self.get_result_display()}"


class CombatInitialization(Event):
    combat = models.OneToOneField(Combat, on_delete=models.CASCADE)

    def _get_fighters_display(self, fighters: set, surprised_fighters: set) -> str:
        """
        Display fighters in a human readable format, in combat event messages.
        """
        fighters_display_list = []
        for fighter in fighters:
            if fighter in surprised_fighters:
                fighters_display_list.append(f"{str(fighter)} (surprised)")
            else:
                fighters_display_list.append(str(fighter))
        return ", ".join(fighters_display_list)

    def get_message(self):
        fighters = self.combat.fighter_set.all()
        surprised_fighters = self.combat.fighter_set.filter(is_surprised=True)
        return f"Combat! {self._get_fighters_display(fighters, surprised_fighters)}"


class CombatInitiativeRequest(Event):
    fighter = models.OneToOneField(Fighter, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=RollStatus, default=RollStatus.PENDING
    )

    def get_message(self):
        return f"{self.fighter} needs to perform a {AbilityName.DEXTERITY} check!"


class CombatInitiativeResponse(Event):
    request = models.OneToOneField(CombatInitiativeRequest, on_delete=models.CASCADE)

    def get_message(self):
        return f"{self.request.fighter.character} performed a dexterity check!"


class CombatInitiativeResult(Event):
    fighter = models.OneToOneField(Fighter, on_delete=models.CASCADE)
    request = models.OneToOneField(CombatInitiativeRequest, on_delete=models.CASCADE)
    response = models.OneToOneField(CombatInitiativeResponse, on_delete=models.CASCADE)
    score = models.SmallIntegerField()

    def get_message(self):
        return f"[{self.fighter.character.user}]'s score: {self.score}"


class CombatInitativeOrderSet(Event):
    combat = models.OneToOneField(Combat, on_delete=models.CASCADE)

    def get_message(self):
        return f"Initiative order: {self.combat.get_initiative_order()}"
