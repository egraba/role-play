class EventSchemaValidationError(Exception):
    pass


class InvalidRoll(Exception):
    """
    Raised when roll parameters are not valid.
    """

    pass


class UnsupportedActor(Exception):
    pass


class UserHasNoCharacter(Exception):
    pass


class ActionNotAvailable(Exception):
    """Raised when trying to use an action that's not available."""

    pass


class NotYourTurn(Exception):
    """Raised when a player tries to act outside their turn."""

    pass
