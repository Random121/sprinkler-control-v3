class SprinklerException(Exception):
    """
    Base exception class for all exceptions raised in this project
    It allows a general catch-all for exceptions used
    """


class InvalidRelay(SprinklerException):
    """
    This exception is raised when the relay ID specified
    is not a relay of the board
    """


class InvalidRelayDuration(SprinklerException):
    """
    This exception is raised when the duration to enable a relay
    is less than or equal to 0
    """


class InvalidActionRequest(SprinklerException):
    """
    This exception is raised when the action request being parsed is malformed
    """


class InvalidAction(SprinklerException):
    """
    This exception is raised when the action sent within the
    action request is invalid
    """


class MissingRequiredArgument(SprinklerException):
    """
    This exception is raised by the parser when a required argument is missing
    from the argument list of an action request
    """


# new


class MissingArgument(SprinklerException):
    """
    This exception is raised when a required argument is missing
    """
