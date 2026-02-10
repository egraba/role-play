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
from ..schemas import EventType
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

    @abstractmethod
    def get_message(self):
        """
        Retrieve messages of an event.

        Messages represent "logs" of an event.
        Messages are not stored in database, only event content is.
        """
        pass

    def get_event_type(self) -> EventType:
        """
        Return the EventType for this event.

        Override in subclasses. Default raises NotImplementedError.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_event_type()"
        )


class GameStart(Event):
    def get_message(self):
        return "The game started."

    def get_event_type(self) -> EventType:
        return EventType.GAME_START


class UserInvitation(Event):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_message(self):
        return f"{self.user} was added to the game."

    def get_event_type(self) -> EventType:
        return EventType.MESSAGE


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

    def get_event_type(self) -> EventType:
        return EventType.MESSAGE


class QuestUpdate(Event):
    quest = models.OneToOneField(Quest, on_delete=models.CASCADE)

    def __str__(self):
        return self.quest.environment[:10]

    def get_message(self):
        return "The Master updated the quest."

    def get_event_type(self) -> EventType:
        return EventType.QUEST_UPDATE


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

    def get_event_type(self) -> EventType:
        if self.roll_type == RollType.ABILITY_CHECK:
            return EventType.ABILITY_CHECK_REQUEST
        elif self.roll_type == RollType.SAVING_THROW:
            return EventType.SAVING_THROW_REQUEST
        raise ValueError(f"Unsupported roll_type: {self.roll_type}")


class RollResponse(Event):
    request = models.ForeignKey(RollRequest, on_delete=models.CASCADE)

    def get_message(self):
        return f"{self.request.player} performed an ability check!"

    def get_event_type(self) -> EventType:
        if self.request.roll_type == RollType.ABILITY_CHECK:
            return EventType.ABILITY_CHECK_RESPONSE
        elif self.request.roll_type == RollType.SAVING_THROW:
            return EventType.SAVING_THROW_RESPONSE
        raise ValueError(f"Unsupported roll_type: {self.request.roll_type}")


class RollResult(Event):
    request = models.ForeignKey(RollRequest, on_delete=models.CASCADE)
    response = models.ForeignKey(RollResponse, on_delete=models.CASCADE)
    score = models.SmallIntegerField()
    result = models.CharField(max_length=1, choices=RollResultType)

    def get_message(self):
        return f"{self.request.player}'s score: {self.score}, \
            {self.request.get_roll_type_display()} result: {self.get_result_display()}"

    def get_event_type(self) -> EventType:
        if self.request.roll_type == RollType.ABILITY_CHECK:
            return EventType.ABILITY_CHECK_RESULT
        elif self.request.roll_type == RollType.SAVING_THROW:
            return EventType.SAVING_THROW_RESULT
        raise ValueError(f"Unsupported roll_type: {self.request.roll_type}")


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
        fighters_display = self._get_fighters_display(fighters, surprised_fighters)
        if fighters.count() > 1:
            return f"Combat! Initiative order: {fighters_display}"
        return f"Combat! {fighters_display}"

    def get_event_type(self) -> EventType:
        return EventType.COMBAT_INITIALIZATION


class CombatInitiativeRequest(Event):
    fighter = models.OneToOneField(Fighter, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=RollStatus, default=RollStatus.PENDING
    )

    def get_message(self):
        return f"{self.fighter} needs to perform a {AbilityName.DEXTERITY} check!"

    def get_event_type(self) -> EventType:
        return EventType.COMBAT_INITIATIVE_REQUEST


class CombatInitiativeResponse(Event):
    request = models.OneToOneField(CombatInitiativeRequest, on_delete=models.CASCADE)

    def get_message(self):
        return f"{self.request.fighter.character} performed a dexterity check!"

    def get_event_type(self) -> EventType:
        return EventType.COMBAT_INITIATIVE_RESPONSE


class CombatInitiativeResult(Event):
    fighter = models.OneToOneField(Fighter, on_delete=models.CASCADE)
    request = models.OneToOneField(CombatInitiativeRequest, on_delete=models.CASCADE)
    response = models.OneToOneField(CombatInitiativeResponse, on_delete=models.CASCADE)
    score = models.SmallIntegerField()

    def get_message(self):
        return f"{self.fighter.character.name}'s initiative roll: {self.score}"

    def get_event_type(self) -> EventType:
        return EventType.COMBAT_INITIATIVE_RESULT


class CombatInitativeOrderSet(Event):
    combat = models.OneToOneField(Combat, on_delete=models.CASCADE)

    def get_message(self):
        order = self.combat.get_initiative_order()
        names = [f"{f.character.name} ({f.dexterity_check})" for f in order]
        return f"Initiative order: {', '.join(names)}"

    def get_event_type(self) -> EventType:
        return EventType.COMBAT_INITIALIZATION_COMPLETE


class CombatStarted(Event):
    """Event fired when combat officially starts after all initiative is rolled."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="combat_started_events"
    )

    def get_message(self):
        return "Combat has begun! Roll for initiative order has been determined."

    def get_event_type(self) -> EventType:
        return EventType.COMBAT_STARTED


class TurnStarted(Event):
    """Event fired when a fighter's turn begins."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="turn_started_events"
    )
    fighter = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="turn_started_events"
    )
    round_number = models.PositiveSmallIntegerField()

    def get_message(self):
        return f"Round {self.round_number}: {self.fighter.character.name}'s turn!"

    def get_event_type(self) -> EventType:
        return EventType.TURN_STARTED


class TurnEnded(Event):
    """Event fired when a fighter's turn ends."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="turn_ended_events"
    )
    fighter = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="turn_ended_events"
    )
    round_number = models.PositiveSmallIntegerField()

    def get_message(self):
        return f"{self.fighter.character.name}'s turn has ended."

    def get_event_type(self) -> EventType:
        return EventType.TURN_ENDED


class RoundEnded(Event):
    """Event fired when a combat round ends."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="round_ended_events"
    )
    round_number = models.PositiveSmallIntegerField()

    def get_message(self):
        return f"Round {self.round_number} has ended."

    def get_event_type(self) -> EventType:
        return EventType.ROUND_ENDED


class CombatEnded(Event):
    """Event fired when combat ends."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="combat_ended_events"
    )

    def get_message(self):
        return "Combat has ended."

    def get_event_type(self) -> EventType:
        return EventType.COMBAT_ENDED


class ActionTaken(Event):
    """Event fired when a fighter takes an action during their turn."""

    combat = models.ForeignKey(
        Combat, on_delete=models.CASCADE, related_name="action_events"
    )
    fighter = models.ForeignKey(
        Fighter, on_delete=models.CASCADE, related_name="action_events"
    )
    turn_action = models.OneToOneField(TurnAction, on_delete=models.CASCADE)

    def get_message(self):
        target = (
            f" targeting {self.turn_action.target_fighter}"
            if self.turn_action.target_fighter
            else ""
        )
        action_type = self.turn_action.get_action_type_display()
        action = self.turn_action.get_action_display()
        return f"{self.fighter.character.name} used {action} ({action_type}){target}."

    def get_event_type(self) -> EventType:
        return EventType.ACTION_TAKEN


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

    def get_message(self):
        target_names = ", ".join(t.name for t in self.targets.all())
        if target_names:
            return f"{self.caster.name} cast {self.spell.name} on {target_names}."
        return f"{self.caster.name} cast {self.spell.name}."

    def get_event_type(self) -> EventType:
        return EventType.SPELL_CAST


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

    def get_message(self):
        return (
            f"{self.target.name} took {self.damage} {self.damage_type} damage "
            f"from {self.spell.name}."
        )

    def get_event_type(self) -> EventType:
        return EventType.SPELL_DAMAGE_DEALT


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

    def get_message(self):
        return (
            f"{self.target.name} was healed for {self.healing} HP by {self.spell.name}."
        )

    def get_event_type(self) -> EventType:
        return EventType.SPELL_HEALING_RECEIVED


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

    def get_message(self):
        return f"{self.target.name} is now {self.condition} from {self.spell.name}."

    def get_event_type(self) -> EventType:
        return EventType.SPELL_CONDITION_APPLIED


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

    def get_message(self):
        result = "succeeded" if self.success else "failed"
        return (
            f"{self.target.name} {result} a {self.save_type} save (DC {self.dc}) "
            f"against {self.spell.name} with a {self.roll}."
        )

    def get_event_type(self) -> EventType:
        return EventType.SPELL_SAVING_THROW


class DiceRoll(Event):
    """Event for a generic dice roll."""

    dice_notation = models.CharField(max_length=20)  # e.g., "3d6"
    dice_type = models.SmallIntegerField()  # 4, 6, 8, 10, 12, 20
    num_dice = models.SmallIntegerField(default=1)
    modifier = models.SmallIntegerField(default=0)
    individual_rolls = models.JSONField()  # [3, 5, 2]
    total = models.SmallIntegerField()
    roll_purpose = models.CharField(max_length=50, blank=True)

    def get_message(self):
        author_name = str(self.author)
        if hasattr(self.author, "master"):
            author_name = "The Master"
        purpose = f" for {self.roll_purpose}" if self.roll_purpose else ""
        modifier_str = ""
        if self.modifier > 0:
            modifier_str = f"+{self.modifier}"
        elif self.modifier < 0:
            modifier_str = str(self.modifier)
        return (
            f"{author_name} rolled {self.dice_notation}{modifier_str}{purpose}: "
            f"{self.individual_rolls} = {self.total}"
        )

    def get_event_type(self) -> EventType:
        return EventType.DICE_ROLL


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

    def get_message(self):
        return (
            f"{self.character.name} must make a DC {self.dc} Constitution save "
            f"to maintain concentration on {self.spell.name}!"
        )

    def get_event_type(self) -> EventType:
        return EventType.CONCENTRATION_SAVE_REQUIRED


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

    def get_message(self):
        result = "maintained" if self.success else "lost"
        return (
            f"{self.character.name} rolled {self.roll} + {self.modifier} = {self.total} "
            f"vs DC {self.dc} and {result} concentration on {self.spell.name}!"
        )

    def get_event_type(self) -> EventType:
        return EventType.CONCENTRATION_SAVE_RESULT


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

    def get_message(self):
        return f"{self.character.name} lost concentration on {self.spell.name}: {self.reason}"

    def get_event_type(self) -> EventType:
        return EventType.CONCENTRATION_BROKEN


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

    def get_message(self):
        return f"{self.character.name} is now concentrating on {self.spell.name}."

    def get_event_type(self) -> EventType:
        return EventType.CONCENTRATION_STARTED
