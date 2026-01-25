from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from pydantic import ValidationError

from character.models.character import Character

from .constants.events import RollType
from .exceptions import EventSchemaValidationError
from .models.game import Game
from .schemas import EventOrigin, EventSchema, EventType
from .services import GameEventService


class GameEventsConsumer(JsonWebsocketConsumer):
    """
    GameEventsConsumer class.

    Attributes:
        user (User): Logged user.
        game (Game): Current game instance.
    """

    def connect(self):
        # self.scope is set in parent's connect()
        self.user = self.scope["user"]
        # The game ID has to be retrieved to create a channel.
        # There is one room per game.
        game_id = self.scope["url_route"]["kwargs"]["game_id"]
        try:
            self.game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            self.close(reason=f"Game of {game_id=} not found")
            return
        self.game_group_name = f"game_{self.game.id}_events"
        async_to_sync(self.channel_layer.group_add)(
            self.game_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, code=None):
        if hasattr(self, "game_group_name"):
            async_to_sync(self.channel_layer.group_discard)(
                self.game_group_name, self.channel_name
            )

    def receive_json(self, content, **kwargs):
        try:
            EventSchema(**content)
        except ValidationError as exc:
            raise EventSchemaValidationError(exc.errors()) from exc

        # Server-side events are already processed, just forward to group
        if content.get("origin") == EventOrigin.SERVER_SIDE:
            async_to_sync(self.channel_layer.group_send)(self.game_group_name, content)
            return

        # Client-side events: save to DB first, then broadcast
        match content["type"]:
            case EventType.MESSAGE:
                # Service saves to DB and broadcasts via send_to_channel
                GameEventService.create_message(
                    game=self.game,
                    user=self.user,
                    content=content["message"],
                    date=content["date"],
                )
                return  # Service handles broadcast

            case EventType.ABILITY_CHECK_RESPONSE:
                try:
                    character = GameEventService.get_character(self.user)
                except Character.DoesNotExist:
                    self.close(reason="Character not found")
                    return
                GameEventService.process_roll(
                    game=self.game,
                    player=character.player,
                    date=content["date"],
                    roll_type=RollType.ABILITY_CHECK,
                )
                return  # Service handles broadcast

            case EventType.SAVING_THROW_RESPONSE:
                try:
                    character = GameEventService.get_character(self.user)
                except Character.DoesNotExist:
                    self.close(reason="Character not found")
                    return
                GameEventService.process_roll(
                    game=self.game,
                    player=character.player,
                    date=content["date"],
                    roll_type=RollType.SAVING_THROW,
                )
                return  # Service handles broadcast

            case EventType.COMBAT_INITIATIVE_RESPONSE:
                try:
                    character = GameEventService.get_character(self.user)
                except Character.DoesNotExist:
                    self.close(reason="Character not found")
                    return
                GameEventService.process_combat_initiative_roll(
                    game=self.game,
                    player=character.player,
                    date=content["date"],
                )
                return  # Service handles broadcast

            case _:
                # For unhandled client events, forward to group
                async_to_sync(self.channel_layer.group_send)(
                    self.game_group_name, content
                )

    def message(self, event):
        """Message typed by player or master on the keyboard."""
        self.send_json(event)

    def game_start(self, event):
        """Message notifying that the game has started."""
        self.send_json(event)

    def quest_update(self, event):
        """Message notifying that the game's quest has been updated by the master."""
        self.send_json(event)

    def ability_check_request(self, event):
        """Ability check request from the master."""
        self.send_json(event)

    def ability_check_response(self, event):
        """Ability check roll from the player."""
        self.send_json(event)

    def ability_check_result(self, event):
        """Ability check result."""
        self.send_json(event)

    def saving_throw_request(self, event):
        """Saving throw request from the master."""
        self.send_json(event)

    def saving_throw_response(self, event):
        """Saving throw roll from the player."""
        self.send_json(event)

    def saving_throw_result(self, event):
        """Saving throw result."""
        self.send_json(event)

    def combat_initialization(self, event):
        """Combat initialization."""
        self.send_json(event)

    def combat_initiative_request(self, event):
        """
        All players have to perform a dexterity check to determine combat order.
        """
        self.send_json(event)

    def combat_initiative_response(self, event):
        """Dexterity check roll from the player."""
        self.send_json(event)

    def combat_initiative_result(self, event):
        """Dexterity check roll result."""
        self.send_json(event)

    def combat_initialization_complete(self, event):
        """Combat initialization complete."""
        self.send_json(event)

    def combat_started(self, event):
        """Combat has officially started."""
        self.send_json(event)

    def turn_started(self, event):
        """A fighter's turn has started."""
        self.send_json(event)

    def turn_ended(self, event):
        """A fighter's turn has ended."""
        self.send_json(event)

    def round_ended(self, event):
        """A combat round has ended."""
        self.send_json(event)

    def combat_ended(self, event):
        """Combat has ended."""
        self.send_json(event)

    def action_taken(self, event):
        """A fighter has taken an action."""
        self.send_json(event)

    def spell_cast(self, event):
        """A spell has been cast."""
        self.send_json(event)

    def spell_damage_dealt(self, event):
        """Spell damage has been dealt."""
        self.send_json(event)

    def spell_healing_received(self, event):
        """Spell healing has been received."""
        self.send_json(event)

    def spell_condition_applied(self, event):
        """A spell condition has been applied."""
        self.send_json(event)

    def spell_saving_throw(self, event):
        """A spell saving throw has been made."""
        self.send_json(event)
