from django.db import models

from ..constants.combat import CombatAction, CombatState
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

        # Create first round
        Round.objects.create(combat=self, number=1)

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
    action = models.CharField(max_length=20, choices=CombatAction.choices, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["round__number"]

    def __str__(self):
        return f"{self.fighter} - Round {self.round.number}"


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
