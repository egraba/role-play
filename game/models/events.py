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
from .combat import Combat, Fighter, TurnAction
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


class GameStart(Event):
    pass


class UserInvitation(Event):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Message(Event):
    content = models.CharField(max_length=100)

    def __str__(self):
        return self.content


class QuestUpdate(Event):
    quest = models.OneToOneField(Quest, on_delete=models.CASCADE)

    def __str__(self):
        return self.quest.environment[:10]


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


class RollResponse(Event):
    request = models.ForeignKey(RollRequest, on_delete=models.CASCADE)


class RollResult(Event):
    request = models.ForeignKey(RollRequest, on_delete=models.CASCADE)
    response = models.ForeignKey(RollResponse, on_delete=models.CASCADE)
    score = models.SmallIntegerField()
    result = models.CharField(max_length=1, choices=RollResultType)


class CombatInitialization(Event):
    combat = models.OneToOneField(Combat, on_delete=models.CASCADE)


class CombatInitiativeRequest(Event):
    fighter = models.OneToOneField(Fighter, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=RollStatus, default=RollStatus.PENDING
    )


class CombatInitiativeResponse(Event):
    request = models.OneToOneField(CombatInitiativeRequest, on_delete=models.CASCADE)


class CombatInitiativeResult(Event):
    fighter = models.OneToOneField(Fighter, on_delete=models.CASCADE)
    request = models.OneToOneField(CombatInitiativeRequest, on_delete=models.CASCADE)
    response = models.OneToOneField(CombatInitiativeResponse, on_delete=models.CASCADE)
    score = models.SmallIntegerField()


class CombatInitativeOrderSet(Event):
    combat = models.OneToOneField(Combat, on_delete=models.CASCADE)


class CombatStarted(Event):
    """Event fired when combat officially starts after all initiative is rolled."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="combat_started_events"
    )


class TurnStarted(Event):
    """Event fired when a fighter's turn begins."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="turn_started_events"
    )
    fighter = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="turn_started_events"
    )
    round_number = models.PositiveSmallIntegerField()


class TurnEnded(Event):
    """Event fired when a fighter's turn ends."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="turn_ended_events"
    )
    fighter = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="turn_ended_events"
    )
    round_number = models.PositiveSmallIntegerField()


class RoundEnded(Event):
    """Event fired when a combat round ends."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="round_ended_events"
    )
    round_number = models.PositiveSmallIntegerField()


class CombatEnded(Event):
    """Event fired when combat ends."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="combat_ended_events"
    )


class ActionTaken(Event):
    """Event fired when a fighter takes an action during their turn."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="action_events"
    )
    fighter = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="action_events"
    )
    turn_action = models.OneToOneField(TurnAction, on_delete=models.CASCADE)


class SpellCast(Event):
    """Event when a spell is cast."""

    caster = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="spell_cast_events",
    )
    spell = models.ForeignKey(
        "magic.SpellSettings",
        on_delete=models.CASCADE,
        related_name="cast_events",
    )
    slot_level = models.PositiveSmallIntegerField()
    targets = models.ManyToManyField(
        "character.Character",
        related_name="targeted_by_spell_events",
    )


class SpellDamageDealt(Event):
    """Event when spell damage is dealt."""

    spell = models.ForeignKey(
        "magic.SpellSettings",
        on_delete=models.CASCADE,
        related_name="damage_events",
    )
    target = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="spell_damage_received_events",
    )
    damage = models.PositiveIntegerField()
    damage_type = models.CharField(max_length=20)


class SpellHealingReceived(Event):
    """Event when spell healing is received."""

    spell = models.ForeignKey(
        "magic.SpellSettings",
        on_delete=models.CASCADE,
        related_name="healing_events",
    )
    target = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="spell_healing_received_events",
    )
    healing = models.PositiveIntegerField()


class SpellConditionApplied(Event):
    """Event when a spell applies a condition."""

    spell = models.ForeignKey(
        "magic.SpellSettings",
        on_delete=models.CASCADE,
        related_name="condition_events",
    )
    target = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="spell_condition_events",
    )
    condition = models.ForeignKey(
        "character.Condition",
        on_delete=models.CASCADE,
        related_name="spell_applied_events",
    )


class SpellSavingThrow(Event):
    """Event recording a spell saving throw."""

    spell = models.ForeignKey(
        "magic.SpellSettings",
        on_delete=models.CASCADE,
        related_name="saving_throw_events",
    )
    target = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="spell_save_events",
    )
    save_type = models.CharField(max_length=5)
    dc = models.PositiveSmallIntegerField()
    roll = models.PositiveSmallIntegerField()
    success = models.BooleanField()


class DiceRoll(Event):
    """Event for a generic dice roll."""

    dice_notation = models.CharField(max_length=20)  # e.g., "3d6"
    dice_type = models.SmallIntegerField()  # 4, 6, 8, 10, 12, 20
    num_dice = models.SmallIntegerField(default=1)
    modifier = models.SmallIntegerField(default=0)
    individual_rolls = models.JSONField()  # [3, 5, 2]
    total = models.SmallIntegerField()
    roll_purpose = models.CharField(max_length=50, blank=True)


class ConcentrationSaveRequired(Event):
    """Event when a character needs to make a concentration save."""

    character = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="concentration_save_events",
    )
    spell = models.ForeignKey(
        "magic.SpellSettings",
        on_delete=models.CASCADE,
        related_name="concentration_check_events",
    )
    damage_taken = models.PositiveSmallIntegerField()
    dc = models.PositiveSmallIntegerField()


class ConcentrationSaveResult(Event):
    """Event recording the result of a concentration save."""

    character = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="concentration_save_result_events",
    )
    spell = models.ForeignKey(
        "magic.SpellSettings",
        on_delete=models.CASCADE,
        related_name="concentration_result_events",
    )
    dc = models.PositiveSmallIntegerField()
    roll = models.PositiveSmallIntegerField()
    modifier = models.SmallIntegerField()
    total = models.SmallIntegerField()
    success = models.BooleanField()


class ConcentrationBroken(Event):
    """Event when concentration is broken."""

    character = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="concentration_broken_events",
    )
    spell = models.ForeignKey(
        "magic.SpellSettings",
        on_delete=models.CASCADE,
        related_name="broken_concentration_events",
    )
    reason = models.CharField(max_length=100)


class ConcentrationStarted(Event):
    """Event when concentration begins on a spell."""

    character = models.ForeignKey(
        "character.Character",
        on_delete=models.CASCADE,
        related_name="concentration_started_events",
    )
    spell = models.ForeignKey(
        "magic.SpellSettings",
        on_delete=models.CASCADE,
        related_name="started_concentration_events",
    )
