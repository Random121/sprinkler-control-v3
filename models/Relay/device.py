from gpiozero import OutputDevice, Factory

from models.Events import EventEmitter
from .timer import BetterTimer
from exceptions import InvalidRelayDuration


class RelayDevice(OutputDevice):
    def __init__(
        self,
        pin: int = None,
        active_high: bool = True,
        initial_value: bool = False,
        pin_factory: Factory = None,
        event_emitter: EventEmitter = None,
    ):
        self._timer: BetterTimer = None
        self._event_emitter = event_emitter
        super().__init__(pin, active_high, initial_value, pin_factory)

    def _emit_update(self):
        if self._event_emitter:
            self._event_emitter.emit("relay_update")

    def enable(self, duration: float = None):
        self.cancel_timer()
        super().on()
        self._emit_update()

        if duration:
            if duration < 0:
                raise InvalidRelayDuration(duration)
            self._timer = BetterTimer(duration, self.disable)
            self._timer.start()

    def disable(self):
        self.cancel_timer()
        super().off()
        self._emit_update()

    def cancel_timer(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None
            self._emit_update()

    @property
    def info(self) -> dict:
        return {
            "is_active": self.is_active,
            "time_elapsed": self.time_elapsed,
            "time_remaining": self.time_remaining,
        }

    @property
    def time_remaining(self) -> float:
        return self._timer.remaining if self._timer else None

    @property
    def time_elapsed(self) -> float:
        return self._timer.elapsed if self._timer else None

    @property
    def value(self) -> int:
        return super().value

    @value.setter
    def value(self, value: int):
        super()._write(value)

    @property
    def is_active(self) -> bool:
        return super().is_active
