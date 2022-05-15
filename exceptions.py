class InvalidRelay(Exception):
    """
    This exception is raised when the relay ID specified
    is not a relay of the board
    """

class InvalidRelayDuration(Exception):
    """
    This exception is raised when the duration to enable a relay
    is below or equal to 0
    """