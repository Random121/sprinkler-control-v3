from threading import Timer
from time import perf_counter
from typing import Callable


class BetterTimer(Timer):
    def __init__(
        self,
        interval: float,
        function: Callable,
        args=None,
        kwargs=None,
    ) -> None:
        super().__init__(interval, function, args, kwargs)
        self.started_at = None

    def start(self) -> None:
        self.started_at = perf_counter()
        super().start()

    @property
    def is_finished(self) -> bool:
        return self.finished.is_set()

    @property
    def elapsed(self) -> float:
        return perf_counter() - self.started_at

    @property
    def remaining(self) -> float:
        return self.interval - self.elapsed
