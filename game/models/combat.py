from django.db import models

from ..constants.combat import ActionType, CombatAction, CombatState
from ..exceptions import ActionNotAvailable
from .game import Game, Player


class Combat(models.Model):
    """Represents a combat encounter in the game."""

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    state = models.CharField(
        max_length=2,
        choices=CombatState.choices,
        default=CombatState.ROLLING_INITIATIVE,
    )
    current_round = models.PositiveSmallIntegerField(default=0)
    current_fighter = models.ForeignKey(
        "Fighter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_turn_combat",
    )
    current_turn_index = models.PositiveSmallIntegerField(default=0)

    def get_initiative_order(self):
        """
        Collects all dexterity checks from fighters, sort them and return
        the order of turns during combat.
        """
        return list(self.fighter_set.all().order_by("-dexterity_check"))

    def all_initiative_rolled(self) -> bool:
        """Check if all fighters have rolled initiative."""
        return not self.fighter_set.filter(dexterity_check__isnull=True).exists()

    def start_combat(self) -> "Fighter | None":
        """
        Start combat after all initiative has been rolled.
        Sets current round to 1 and current fighter to first in initiative order.
        Returns the first fighter or None if no fighters.
        """
        if not self.all_initiative_rolled():
            return None

        initiative_order = self.get_initiative_order()
        if not initiative_order:
            return None

        self.state = CombatState.ACTIVE
        self.current_round = 1
        self.current_turn_index = 0
        self.current_fighter = initiative_order[0]
        self.save()

        # Create first round and turn
        first_round = Round.objects.create(combat=self, number=1)
        Turn.objects.create(
            fighter=self.current_fighter,
            round=first_round,
            movement_total=self.current_fighter.character.speed or 30,
        )

        return self.current_fighter

    def advance_turn(self) -> tuple["Fighter | None", bool]:
        """
        Advance to the next fighter's turn.
        Returns (next_fighter, is_new_round).
        If combat has ended, returns (None, False).
        """
        if self.state != CombatState.ACTIVE:
            return None, False

        initiative_order = self.get_initiative_order()
        if not initiative_order:
            return None, False

        # Mark current turn as completed
        current_turn = Turn.objects.filter(
            fighter=self.current_fighter,
            round__combat=self,
            completed=False,
        ).first()
        if current_turn:
            current_turn.completed = True
            current_turn.save()

        # Move to next fighter
        self.current_turn_index += 1
        is_new_round = False

        # Check if we've gone through all fighters (new round)
        if self.current_turn_index >= len(initiative_order):
            self.current_turn_index = 0
            self.current_round += 1
            is_new_round = True
            Round.objects.create(combat=self, number=self.current_round)

        self.current_fighter = initiative_order[self.current_turn_index]
        self.save()

        # Create turn for next fighter
        current_round = Round.objects.get(combat=self, number=self.current_round)
        Turn.objects.create(
            fighter=self.current_fighter,
            round=current_round,
            movement_total=self.current_fighter.character.speed or 30,
        )

        return self.current_fighter, is_new_round

    def end_combat(self) -> None:
        """End the combat encounter."""
        self.state = CombatState.ENDED
        self.current_fighter = None
        self.save()

    def get_turn_order_display(self) -> list[dict]:
        """Get a list of fighters with their initiative scores for display."""
        return [
            {
                "fighter": fighter,
                "initiative": fighter.dexterity_check,
                "is_current": fighter == self.current_fighter,
                "is_surprised": fighter.is_surprised,
            }
            for fighter in self.get_initiative_order()
        ]


class Round(models.Model):
    """Represents a round within a combat encounter."""

    combat = models.ForeignKey(Combat, on_delete=models.CASCADE, related_name="rounds")
    number = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["number"]
        unique_together = ["combat", "number"]

    def __str__(self):
        return f"Round {self.number}"


class Turn(models.Model):
    """Represents a single turn within a combat round."""

    fighter = models.ForeignKey(
        "Fighter", on_delete=models.CASCADE, null=True, blank=True
    )
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name="turns")

    # Action economy tracking
    action_used = models.BooleanField(default=False)
    bonus_action_used = models.BooleanField(default=False)
    reaction_used = models.BooleanField(default=False)
    movement_used = models.PositiveSmallIntegerField(default=0)
    movement_total = models.PositiveSmallIntegerField(default=30)

    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["round__number"]

    def __str__(self):
        return f"{self.fighter} - Round {self.round.number}"

    def can_take_action(self) -> bool:
        """Check if the standard action is still available."""
        return not self.action_used

    def can_take_bonus_action(self) -> bool:
        """Check if the bonus action is still available."""
        return not self.bonus_action_used

    def can_take_reaction(self) -> bool:
        """Check if the reaction is still available."""
        return not self.reaction_used

    def remaining_movement(self) -> int:
        """Get remaining movement in feet."""
        return self.movement_total - self.movement_used

    def use_action(
        self, action: CombatAction, target: "Fighter | None" = None
    ) -> "TurnAction":
        """Use the standard action for this turn."""
        if self.action_used:
            raise ActionNotAvailable("Action already used this turn")
        self.action_used = True
        self.save()
        return TurnAction.objects.create(
            turn=self,
            action_type=ActionType.ACTION,
            action=action,
            target_fighter=target,
        )

    def use_bonus_action(
        self, action: CombatAction, target: "Fighter | None" = None
    ) -> "TurnAction":
        """Use the bonus action for this turn."""
        if self.bonus_action_used:
            raise ActionNotAvailable("Bonus action already used this turn")
        self.bonus_action_used = True
        self.save()
        return TurnAction.objects.create(
            turn=self,
            action_type=ActionType.BONUS_ACTION,
            action=action,
            target_fighter=target,
        )

    def use_reaction(
        self, action: CombatAction, target: "Fighter | None" = None
    ) -> "TurnAction":
        """Use the reaction for this turn."""
        if self.reaction_used:
            raise ActionNotAvailable("Reaction already used this turn")
        self.reaction_used = True
        self.save()
        return TurnAction.objects.create(
            turn=self,
            action_type=ActionType.REACTION,
            action=action,
            target_fighter=target,
        )

    def use_movement(self, feet: int) -> int:
        """Use movement. Returns actual feet moved (may be limited by remaining)."""
        actual = min(feet, self.remaining_movement())
        self.movement_used += actual
        self.save()
        return actual


class Fighter(models.Model):
    """A fighter represents a character during a combat."""

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    character = models.ForeignKey("character.Character", on_delete=models.CASCADE)
    is_surprised = models.BooleanField(default=False)
    combat = models.ForeignKey(Combat, on_delete=models.CASCADE, null=True, blank=True)
    dexterity_check = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-dexterity_check"]

    def __str__(self):
        return self.character.name


class TurnAction(models.Model):
    """Records a single action taken during a turn."""

    turn = models.ForeignKey(Turn, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=1, choices=ActionType.choices)
    action = models.CharField(max_length=20, choices=CombatAction.choices)
    target_fighter = models.ForeignKey(
        Fighter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="targeted_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        target = f" -> {self.target_fighter}" if self.target_fighter else ""
        return f"{self.get_action_display()}{target}"
