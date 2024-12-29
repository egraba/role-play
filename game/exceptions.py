class EventSchemaValidationError(Exception):
    pass


class InvalidRoll(Exception):
    """
    Raised when roll parameters are not valid.
    """

    pass


class UserHasNoCharacter(Exception):
    pass
