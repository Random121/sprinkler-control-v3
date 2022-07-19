from typing import Union
from gpiozero import Factory

from .device import RelayDevice
from models.Events import EventEmitter
from exceptions import InvalidRelay


class RelayBoard:
    def __init__(
        self,
        pinout: dict[str, int] = None,
        active_high: bool = True,
        initial_value: bool = False,
        pin_factory: Factory = None,
    ) -> None:
        self.emitter = EventEmitter()
        self._relays = {
            id: RelayDevice(
                pin,
                active_high,
                initial_value,
                pin_factory,
                lambda: self.emitter.emit("update", id),
            )
            for id, pin in pinout.items()
        }

    #################
    # Private methods
    #################

    def _enable(self, ids: list = None, duration: float = None):
        if ids is None:
            for relay in self._relays.values():
                relay.enable(duration)
        else:
            for id in ids:
                if not self.is_relay(id):
                    raise InvalidRelay(id)
                self._relays[id].enable(duration)

    def _disable(self, ids: list = None):
        if ids is None:
            for relay in self._relays.values():
                relay.disable()
        else:
            for id in ids:
                if not self.is_relay(id):
                    raise InvalidRelay(id)
                self._relays[id].disable()

    def _cancel_timer(self, ids: list = None):
        if ids is None:
            for relay in self._relays.values():
                relay.cancel_timer()
        else:
            for id in ids:
                if not self.is_relay(id):
                    raise InvalidRelay(id)
                self._relays[id].cancel_timer()

    def _get_info(self, ids: list = None):
        if ids is None:
            return self._get_info(self._relays.keys())

        infos = []

        for id in ids:
            if not self.is_relay(id):
                raise InvalidRelay(id)

            infos.append({"id": id, "info": self._relays[id].info})

        return infos

    ################
    # Public methods
    ################

    def is_relay(self, id: str) -> bool:
        return id in self._relays

    # enable which is safe for raspberry pi
    def enable(self, id: Union[list, str] = None, duration: float = None):
        if id is None or duration is None:
            return

        if isinstance(id, list) and len(id) > 1:
            return

        if isinstance(id, str):
            id = [id]

        self._disable()
        self._enable(id, duration)
        self.emitter.emit("update", id)

    def disable(self, ids: list = None):
        if isinstance(ids, str):
            ids = [ids]

        self._disable(ids)
        self.emitter.emit("update", ids)

    def cancel_timer(self, ids: list = None):
        if isinstance(ids, str):
            ids = [ids]

        self._cancel_timer(ids)
        self.emitter.emit("update", ids)

    def get_info(self, ids: list = None):
        if isinstance(ids, str):
            ids = [ids]

        return self._get_info(ids)

    def get_relay(self, id: str):
        if not self.is_relay(id):
            raise InvalidRelay(id)

        return self._relays[id]
