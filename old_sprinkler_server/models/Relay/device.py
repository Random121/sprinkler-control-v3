from typing import Callable
from gpiozero import OutputDevice, Factory

from .timer import BetterTimer
from exceptions import InvalidRelayDuration


class RelayDevice(OutputDevice):
    def __init__(
        self,
        pin: int = None,
        active_high: bool = True,
        initial_value: bool = False,
        pin_factory: Factory = None,
        timer_end_callback: Callable = None,
    ):
        super().__init__(pin, active_high, initial_value, pin_factory)
        self._timer_end_callback = timer_end_callback
        self._timer: BetterTimer = None

    #################
    # Private methods
    #################

    def _timer_disable(self):
        self.disable()

        if self._timer_end_callback:
            self._timer_end_callback()

    ################
    # Public methods
    ################

    def enable(self, duration: float = None):
        self.cancel_timer()
        super().on()

        if duration is not None:
            if duration <= 0:
                raise InvalidRelayDuration(f"Duration must be greater than 0")

            self._timer = BetterTimer(duration, self._timer_disable)
            self._timer.start()

    def disable(self):
        self.cancel_timer()
        super().off()

    def cancel_timer(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    @property
    def info(self):
        return {
            "is_active": self.is_active,
            "time_elapsed": self.time_elapsed,
            "time_remaining": self.time_remaining,
        }

    @property
    def time_remaining(self) -> float:
        return self._timer.remaining if self._timer is not None else None

    @property
    def time_elapsed(self) -> float:
        return self._timer.elapsed if self._timer is not None else None
