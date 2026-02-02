import random

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View

from character.models.spells import Concentration

from ..models.events import (
    ConcentrationBroken,
    ConcentrationSaveRequired,
    ConcentrationSaveResult,
)
from ..models.game import Actor
from ..utils.channels import send_to_channel
from .mixins import GameContextMixin


class ConcentrationSaveModalView(UserPassesTestMixin, GameContextMixin, View):
    """View for displaying the concentration save modal."""

    def test_func(self):
        """Verify the user has access to this game."""
        return self.is_user_player() or self.is_user_master()

    def get(self, request, *args, **kwargs):
        """Show the concentration save modal."""
        character_id = kwargs.get("character_id")
        damage = int(request.GET.get("damage", 0))

        from character.models import Character

        try:
            character = Character.objects.get(pk=character_id)
        except Character.DoesNotExist:
            return HttpResponse("Character not found", status=404)

        # Check if character has active concentration
        try:
            concentration = character.concentration
        except Concentration.DoesNotExist:
            return HttpResponse("No active concentration", status=400)

        # Calculate DC: max(10, damage // 2)
        dc = max(10, damage // 2)

        # Get Constitution modifier
        try:
            con_modifier = character.constitution.modifier
        except (AttributeError, Exception):
            con_modifier = 0

        context = {
            "game": self.game,
            "character": character,
            "concentration": concentration,
            "damage": damage,
            "dc": dc,
            "con_modifier": con_modifier,
            "show_modal": True,
        }

        html = render_to_string("game/partials/concentration_save_modal.html", context)
        return HttpResponse(html)


class ConcentrationSaveRollView(UserPassesTestMixin, GameContextMixin, View):
    """View for processing the concentration save roll."""

    def test_func(self):
        """Verify the user has access to this game."""
        return self.is_user_player() or self.is_user_master()

    def post(self, request, *args, **kwargs):
        """Process the concentration save roll."""
        character_id = kwargs.get("character_id")
        dc = int(request.POST.get("dc", 10))
        con_modifier = int(request.POST.get("con_modifier", 0))

        from character.models import Character

        try:
            character = Character.objects.get(pk=character_id)
        except Character.DoesNotExist:
            return HttpResponse("Character not found", status=404)

        # Check if character has active concentration
        try:
            concentration = character.concentration
        except Concentration.DoesNotExist:
            return HttpResponse("No active concentration", status=400)

        # Roll the d20
        roll = random.randint(1, 20)
        total = roll + con_modifier

        # Determine success (natural 20 always succeeds, natural 1 always fails)
        is_natural_20 = roll == 20
        is_natural_1 = roll == 1
        success = is_natural_20 or (not is_natural_1 and total >= dc)

        # Get the author for the event
        try:
            author = Actor.objects.get(
                player__game=self.game, player__user=self.request.user
            )
        except Actor.DoesNotExist:
            # Fallback to master if user is the master
            author = self.game.master

        # Create and broadcast the result event
        result_event = ConcentrationSaveResult.objects.create(
            game=self.game,
            author=author,
            character=character,
            spell=concentration.spell,
            dc=dc,
            roll=roll,
            modifier=con_modifier,
            total=total,
            success=success,
        )
        send_to_channel(result_event)

        # If failed, break concentration
        if not success:
            broken_event = ConcentrationBroken.objects.create(
                game=self.game,
                author=author,
                character=character,
                spell=concentration.spell,
                reason="Failed concentration save",
            )
            concentration.break_concentration()
            send_to_channel(broken_event)

        context = {
            "game": self.game,
            "character": character,
            "spell_name": concentration.spell.name
            if success
            else result_event.spell.name,
            "dc": dc,
            "roll": roll,
            "con_modifier": con_modifier,
            "total": total,
            "success": success,
            "is_natural_20": is_natural_20,
            "is_natural_1": is_natural_1,
            "show_result": True,
            "show_modal": True,
        }

        html = render_to_string("game/partials/concentration_save_modal.html", context)
        response = HttpResponse(html)
        response["HX-Trigger"] = "concentration-updated, initiative-updated"
        return response


def check_concentration_on_damage(game, character, damage, author):
    """
    Check if a character needs to make a concentration save after taking damage.

    Returns a dict with concentration info if save is required, None otherwise.
    """
    try:
        concentration = character.concentration
    except Concentration.DoesNotExist:
        return None

    # Calculate DC
    dc = max(10, damage // 2)

    # Create the event
    event = ConcentrationSaveRequired.objects.create(
        game=game,
        author=author,
        character=character,
        spell=concentration.spell,
        damage_taken=damage,
        dc=dc,
    )
    send_to_channel(event)

    return {
        "character_id": character.pk,
        "spell_name": concentration.spell.name,
        "damage": damage,
        "dc": dc,
    }
