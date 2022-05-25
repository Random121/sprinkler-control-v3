from gpiozero import Factory

from .device import RelayDevice
from models.Events import EventEmitter
from exceptions import InvalidRelay


class RelayBoard:
    def __init__(
        self,
        pinout: dict = None,
        active_high: bool = True,
        initial_value: bool = False,
        pin_factory: Factory = None,
    ):
        self.emitter = EventEmitter()
        self._relays = {
            id: RelayDevice(pin, active_high, initial_value, pin_factory, self.emitter)
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
            return {id: relay.info for id, relay in self._relays.items()}

        infos = {}

        for id in ids:
            if not self.is_relay(id):
                raise InvalidRelay(id)
            infos[id] = self._relays[id].info

        return infos

    ################
    # Public methods
    ################

    def is_relay(self, id: str) -> bool:
        return id in self._relays

    # enable which is safe for raspberry pi
    def enable(self, id: list = None, duration: float = None):
        if id is None or duration is None:
            return

        if isinstance(id, str):
            id = [id]

        self._disable()
        self._enable(id, duration)
        self.emitter.emit("relay_update")

    def disable(self, ids: list = None):
        if isinstance(ids, str):
            ids = [ids]

        self._disable(ids)
        self.emitter.emit("relay_update")

    def cancel_timer(self, ids: list = None):
        if isinstance(ids, str):
            ids = [ids]

        self._cancel_timer(ids)
        self.emitter.emit("relay_update")

    def get_info(self, ids: list = None):
        if isinstance(ids, str):
            ids = [ids]

        infos = self._get_info(ids)

        # make single relay info simpler
        if len(infos) == 1:
            return infos[list(infos)[0]]

        return infos

    def get_relay(self, id: str):
        if not self.is_relay(id):
            raise InvalidRelay(id)

        return self._relays[id]
