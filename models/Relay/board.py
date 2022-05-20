from exceptions import InvalidRelay
from .device import RelayDevice


class RelayBoard:
    def __init__(
        self,
        pinout: dict = None,
        active_high: bool = True,
        initial_value: bool = False,
        pin_factory=None,
    ) -> None:
        self._relays = {
            id: RelayDevice(pin, active_high, initial_value, pin_factory)
            for id, pin in pinout.items()
        }

    def is_relay(self, id: str) -> bool:
        return id in self._relays

    def enable(self, ids: list, duration: float = None):
        for id in ids:
            if not self.is_relay(id):
                raise InvalidRelay(id)

            self.disable()  # raspberry pi can only handle one relay open at once
            self._relays[id].enable(duration)

    def disable(self, ids: list = None):
        if ids is None:
            for relay in self._relays.values():
                relay.disable()
        else:
            for id in ids:
                if not self.is_relay(id):
                    raise InvalidRelay(id)
                self._relays[id].disable()

    def cancel_timer(self, ids: list = None):
        if ids is None:
            for relay in self._relays.values():
                relay.cancel_timer()
        else:
            for id in ids:
                if not self.is_relay(id):
                    raise InvalidRelay(id)
                self._relays[id].cancel_timer()

    def get_info(self, ids: list = None):
        if ids is None:
            return {id: relay.info for id, relay in self._relays.items()}

        info_dict = {}

        for id in ids:
            if not self.is_relay(id):
                raise InvalidRelay(id)
            info_dict[id] = self._relays[id].info

        # make single relay info simpler
        if len(info_dict) == 1:
            return info_dict[list(info_dict)[0]]
        else:
            return info_dict

    def get_relay(self, id: str):
        if not self.is_relay(id):
            raise InvalidRelay(id)
        return self._relays[id]
