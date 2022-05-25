class SprinklerControlBaseException(Exception):
    """
    Base exception class for all exceptions raised in this project
    It allows a general catch-all for exceptions used
    """


class InvalidRelay(SprinklerControlBaseException):
    """
    This exception is raised when the relay ID specified
    is not a relay of the board
    """


class InvalidRelayDuration(SprinklerControlBaseException):
    """
    This exception is raised when the duration to enable a relay
    is less than or equal to 0
    """


class InvalidActionRequest(SprinklerControlBaseException):
    """
    This exception is raised when the action request being parsed is malformed
    """


class InvalidAction(SprinklerControlBaseException):
    """
    This exception is raised when the action sent within the
    action request is invalid
    """


class MissingRequiredArgument(SprinklerControlBaseException):
    """
    This exception is raised by the parser when a required argument is missing
    from the argument list of an action request
    """
