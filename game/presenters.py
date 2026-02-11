from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from character.constants.abilities import AbilityName

from .exceptions import UnsupportedActor

if TYPE_CHECKING:
    from .models.events import Event


def _format_game_start(event: Event) -> str:
    return "The game started."


def _format_user_invitation(event: Event) -> str:
    return f"{event.user} was added to the game."


def _format_message(event: Event) -> str:
    if hasattr(event.author, "master"):
        author_str = "The Master"
    elif hasattr(event.author, "player"):
        author_str = str(event.author)
    else:
        raise UnsupportedActor(f"{type(event.author)} is not supported")
    return f"{author_str} said: {event.content}"


def _format_quest_update(event: Event) -> str:
    return "The Master updated the quest."


def _format_roll_request(event: Event) -> str:
    return f"{event.player} needs to perform a {event.ability_type} check! \
            Difficulty: {event.get_difficulty_class_display()}."


def _format_roll_response(event: Event) -> str:
    return f"{event.request.player} performed an ability check!"


def _format_roll_result(event: Event) -> str:
    return f"{event.request.player}'s score: {event.score}, \
            {event.request.get_roll_type_display()} result: {event.get_result_display()}"


def _get_fighters_display(fighters, surprised_fighters) -> str:
    """Display fighters in a human readable format, in combat event messages."""
    fighters_display_list = []
    for fighter in fighters:
        if fighter in surprised_fighters:
            fighters_display_list.append(f"{str(fighter)} (surprised)")
        else:
            fighters_display_list.append(str(fighter))
    return ", ".join(fighters_display_list)


def _format_combat_initialization(event: Event) -> str:
    fighters = event.combat.fighter_set.all()
    surprised_fighters = event.combat.fighter_set.filter(is_surprised=True)
    fighters_display = _get_fighters_display(fighters, surprised_fighters)
    if fighters.count() > 1:
        return f"Combat! Initiative order: {fighters_display}"
    return f"Combat! {fighters_display}"


def _format_combat_initiative_request(event: Event) -> str:
    return f"{event.fighter} needs to perform a {AbilityName.DEXTERITY} check!"


def _format_combat_initiative_response(event: Event) -> str:
    return f"{event.request.fighter.character} performed a dexterity check!"


def _format_combat_initiative_result(event: Event) -> str:
    return f"{event.fighter.character.name}'s initiative roll: {event.score}"


def _format_combat_initiative_order_set(event: Event) -> str:
    order = event.combat.get_initiative_order()
    names = [f"{f.character.name} ({f.dexterity_check})" for f in order]
    return f"Initiative order: {', '.join(names)}"


def _format_combat_started(event: Event) -> str:
    return "Combat has begun! Roll for initiative order has been determined."


def _format_turn_started(event: Event) -> str:
    return f"Round {event.round_number}: {event.fighter.character.name}'s turn!"


def _format_turn_ended(event: Event) -> str:
    return f"{event.fighter.character.name}'s turn has ended."


def _format_round_ended(event: Event) -> str:
    return f"Round {event.round_number} has ended."


def _format_combat_ended(event: Event) -> str:
    return "Combat has ended."


def _format_action_taken(event: Event) -> str:
    target = (
        f" targeting {event.turn_action.target_fighter}"
        if event.turn_action.target_fighter
        else ""
    )
    action_type = event.turn_action.get_action_type_display()
    action = event.turn_action.get_action_display()
    return f"{event.fighter.character.name} used {action} ({action_type}){target}."


def _format_spell_cast(event: Event) -> str:
    target_names = ", ".join(t.name for t in event.targets.all())
    if target_names:
        return f"{event.caster.name} cast {event.spell.name} on {target_names}."
    return f"{event.caster.name} cast {event.spell.name}."


def _format_spell_damage_dealt(event: Event) -> str:
    return (
        f"{event.target.name} took {event.damage} {event.damage_type} damage "
        f"from {event.spell.name}."
    )


def _format_spell_healing_received(event: Event) -> str:
    return (
        f"{event.target.name} was healed for {event.healing} HP by {event.spell.name}."
    )


def _format_spell_condition_applied(event: Event) -> str:
    return f"{event.target.name} is now {event.condition} from {event.spell.name}."


def _format_spell_saving_throw(event: Event) -> str:
    result = "succeeded" if event.success else "failed"
    return (
        f"{event.target.name} {result} a {event.save_type} save (DC {event.dc}) "
        f"against {event.spell.name} with a {event.roll}."
    )


def _format_dice_roll(event: Event) -> str:
    author_name = str(event.author)
    if hasattr(event.author, "master"):
        author_name = "The Master"
    purpose = f" for {event.roll_purpose}" if event.roll_purpose else ""
    modifier_str = ""
    if event.modifier > 0:
        modifier_str = f"+{event.modifier}"
    elif event.modifier < 0:
        modifier_str = str(event.modifier)
    return (
        f"{author_name} rolled {event.dice_notation}{modifier_str}{purpose}: "
        f"{event.individual_rolls} = {event.total}"
    )


def _format_concentration_save_required(event: Event) -> str:
    return (
        f"{event.character.name} must make a DC {event.dc} Constitution save "
        f"to maintain concentration on {event.spell.name}!"
    )


def _format_concentration_save_result(event: Event) -> str:
    result = "maintained" if event.success else "lost"
    return (
        f"{event.character.name} rolled {event.roll} + {event.modifier} = {event.total} "
        f"vs DC {event.dc} and {result} concentration on {event.spell.name}!"
    )


def _format_concentration_broken(event: Event) -> str:
    return f"{event.character.name} lost concentration on {event.spell.name}: {event.reason}"


def _format_concentration_started(event: Event) -> str:
    return f"{event.character.name} is now concentrating on {event.spell.name}."


# Lazy-built registry mapping Event subclass -> formatter function
_MESSAGE_FORMATTERS: dict[type[Event], Callable[[Event], str]] | None = None


def _build_formatters() -> dict[type[Event], Callable[[Event], str]]:
    from .models.events import (
        ActionTaken,
        CombatEnded,
        CombatInitativeOrderSet,
        CombatInitialization,
        CombatInitiativeRequest,
        CombatInitiativeResponse,
        CombatInitiativeResult,
        CombatStarted,
        ConcentrationBroken,
        ConcentrationSaveRequired,
        ConcentrationSaveResult,
        ConcentrationStarted,
        DiceRoll,
        GameStart,
        Message,
        QuestUpdate,
        RollRequest,
        RollResponse,
        RollResult,
        RoundEnded,
        SpellCast,
        SpellConditionApplied,
        SpellDamageDealt,
        SpellHealingReceived,
        SpellSavingThrow,
        TurnEnded,
        TurnStarted,
        UserInvitation,
    )

    return {
        GameStart: _format_game_start,
        UserInvitation: _format_user_invitation,
        Message: _format_message,
        QuestUpdate: _format_quest_update,
        RollRequest: _format_roll_request,
        RollResponse: _format_roll_response,
        RollResult: _format_roll_result,
        CombatInitialization: _format_combat_initialization,
        CombatInitiativeRequest: _format_combat_initiative_request,
        CombatInitiativeResponse: _format_combat_initiative_response,
        CombatInitiativeResult: _format_combat_initiative_result,
        CombatInitativeOrderSet: _format_combat_initiative_order_set,
        CombatStarted: _format_combat_started,
        TurnStarted: _format_turn_started,
        TurnEnded: _format_turn_ended,
        RoundEnded: _format_round_ended,
        CombatEnded: _format_combat_ended,
        ActionTaken: _format_action_taken,
        SpellCast: _format_spell_cast,
        SpellDamageDealt: _format_spell_damage_dealt,
        SpellHealingReceived: _format_spell_healing_received,
        SpellConditionApplied: _format_spell_condition_applied,
        SpellSavingThrow: _format_spell_saving_throw,
        DiceRoll: _format_dice_roll,
        ConcentrationSaveRequired: _format_concentration_save_required,
        ConcentrationSaveResult: _format_concentration_save_result,
        ConcentrationBroken: _format_concentration_broken,
        ConcentrationStarted: _format_concentration_started,
    }


def format_event_message(event: Event) -> str:
    """Format the display message for an event instance."""
    global _MESSAGE_FORMATTERS  # noqa: PLW0603
    if _MESSAGE_FORMATTERS is None:
        _MESSAGE_FORMATTERS = _build_formatters()

    event_class = type(event)
    formatter = _MESSAGE_FORMATTERS.get(event_class)
    if formatter is None:
        raise NotImplementedError(
            f"{event_class.__name__} must be registered in presenters"
        )
    return formatter(event)
