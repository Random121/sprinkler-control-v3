from typing import Callable
from gpiozero import OutputDevice, Factory

from .timer import BetterTimer


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

    def _timer_end(self):
        self.disable()

        if self._timer_end_callback:
            self._timer_end_callback()

    ################
    # Public methods
    ################

    def enable(self, duration: float = None):
        self.cancel_timer()
        self.on()

        if duration is not None:
            if duration <= 0:
                raise ValueError(f"Duration must be greater than 0: {duration}")

            self._timer = BetterTimer(duration, self._timer_end)
            self._timer.start()

    def disable(self):
        self.cancel_timer()
        self.off()

    def cancel_timer(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    @property
    def state(self):
        return {
            "is_active": self.is_active,
            "time_remaining": self.time_remaining,
            "time_elapsed": self.time_elapsed,
            "duration": self.duration,
        }

    @property
    def time_remaining(self) -> float | None:
        return None if self._timer is None else self._timer.remaining

    @property
    def time_elapsed(self) -> float | None:
        return None if self._timer is None else self._timer.elapsed

    @property
    def duration(self) -> float | None:
        return None if self._timer is None else self._timer.interval
