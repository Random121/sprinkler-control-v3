class SprinklerException(Exception):
    """
    Base exception class for all exceptions raised in this project
    It allows a general catch-all for exceptions used
    """


class MissingArgument(SprinklerException):
    """
    This exception is raised when a required argument is missing
    """
