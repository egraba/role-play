from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from game.schemas import EventOrigin, EventType

from ..models.character import Character


class HPBarMixin:
    """Mixin for HP bar views."""

    def get_character(self, pk: int) -> Character:
        return get_object_or_404(Character, pk=pk)

    def render_hp_bar(self, character: Character, animation: str = "") -> HttpResponse:
        html = render_to_string(
            "character/partials/hp_bar.html",
            {"character": character, "animation": animation},
        )
        response = HttpResponse(html)
        # Add HX-Trigger header to notify other components
        response["HX-Trigger"] = "hp-updated"
        return response

    def broadcast_hp_event(
        self,
        character: Character,
        event_type: EventType,
        message: str,
    ) -> None:
        """Broadcast HP change event to all players in the game via WebSocket."""
        # Check if character is in a game
        if not hasattr(character, "player") or not character.player:
            return
        game = getattr(character.player, "game", None)
        if not game:
            return

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        game_group_name = f"game_{game.id}_events"
        event = {
            "type": event_type.value.replace(".", "_"),
            "username": character.user.username,
            "date": datetime.now().isoformat(),
            "message": message,
            "origin": EventOrigin.SERVER_SIDE,
            "character_id": character.pk,
            "hp": character.hp,
            "max_hp": character.max_hp,
            "temp_hp": character.temp_hp,
        }
        async_to_sync(channel_layer.group_send)(game_group_name, event)


class HPBarView(LoginRequiredMixin, HPBarMixin, View):
    """Get the current HP bar state."""

    def get(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)
        return self.render_hp_bar(character)


class TakeDamageView(LoginRequiredMixin, HPBarMixin, View):
    """Apply damage to a character."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)
        try:
            damage = int(request.POST.get("damage", 0))
        except (TypeError, ValueError):
            damage = 0

        if damage > 0:
            character.take_damage(damage)
            self.broadcast_hp_event(
                character,
                EventType.HP_DAMAGE,
                f"{character.name} took {damage} damage.",
            )

        return self.render_hp_bar(character, animation="damage")


class HealView(LoginRequiredMixin, HPBarMixin, View):
    """Heal a character."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)
        try:
            amount = int(request.POST.get("amount", 0))
        except (TypeError, ValueError):
            amount = 0

        if amount > 0:
            actual = character.heal(amount)
            if actual > 0:
                self.broadcast_hp_event(
                    character,
                    EventType.HP_HEAL,
                    f"{character.name} healed for {actual} HP.",
                )

        return self.render_hp_bar(character, animation="heal")


class AddTempHPView(LoginRequiredMixin, HPBarMixin, View):
    """Add temporary HP to a character."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)
        try:
            amount = int(request.POST.get("amount", 0))
        except (TypeError, ValueError):
            amount = 0

        if amount > 0:
            character.add_temp_hp(amount)
            self.broadcast_hp_event(
                character,
                EventType.HP_TEMP,
                f"{character.name} gained {amount} temporary HP.",
            )

        return self.render_hp_bar(character, animation="temp")


class RemoveTempHPView(LoginRequiredMixin, HPBarMixin, View):
    """Remove temporary HP from a character."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)
        character.remove_temp_hp()
        return self.render_hp_bar(character)


class DeathSaveView(LoginRequiredMixin, HPBarMixin, View):
    """Record a death save result."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)
        result = request.POST.get("result", "")

        if result == "success":
            is_stable = character.add_death_save_success()
            animation = "heal"
            if is_stable:
                message = f"{character.name} is now stable!"
            else:
                message = f"{character.name} succeeded a death save."
            self.broadcast_hp_event(character, EventType.HP_DEATH_SAVE, message)
        elif result == "failure":
            is_dead = character.add_death_save_failure()
            animation = "damage"
            if is_dead:
                message = f"{character.name} has died!"
            else:
                message = f"{character.name} failed a death save."
            self.broadcast_hp_event(character, EventType.HP_DEATH_SAVE, message)
        else:
            animation = ""

        return self.render_hp_bar(character, animation=animation)


class ResetDeathSavesView(LoginRequiredMixin, HPBarMixin, View):
    """Reset death save counters."""

    def post(self, request, pk: int) -> HttpResponse:
        character = self.get_character(pk)
        character.reset_death_saves()
        return self.render_hp_bar(character)
