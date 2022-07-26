import logging
from gpiozero import Factory
from typing import Any

from .device import RelayDevice
from sprinkler_server.models.Events import EventEmitter


class RelayBoard:
    def __init__(
        self,
        pin_mapping: dict[str, int],
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
                # loop variable capture: https://stackoverflow.com/q/1107210
                lambda id=id: self.emitter.emit("update", [id]),
            )
            for id, pin in pin_mapping.items()
        }

    #################
    # Private methods
    #################

    def _enable(self, ids: list = None, duration: float = None):
        if ids is None:
            # all relays
            for relay in self._relays.values():
                relay.enable(duration)
        else:
            # specific relays
            for id in ids:
                self.get_relay(id).enable(duration)

    def _disable(self, ids: list = None):
        if ids is None:
            # all relays
            for relay in self._relays.values():
                relay.disable()
        else:
            # specific relays
            for id in ids:
                self.get_relay(id).disable()

    def _cancel_timer(self, ids: list = None):
        if ids is None:
            # all relays
            for relay in self._relays.values():
                relay.cancel_timer()
        else:
            # specific relays
            for id in ids:
                self.get_relay(id).cancel_timer()

    def _get_state(self, ids: list = None):
        if ids is None:
            return self._get_state(self._relays.keys())

        states = []

        for id in ids:
            states.append({"id": id, "state": self.get_relay(id).state})

        return states

    ################
    # Public methods
    ################

    # extra limitations are added for raspberry pi
    # since it can only handle one relay on at once
    def enable(self, ids: (str | list | None) = None, duration: float = None):
        # normalize ids
        if isinstance(ids, str):
            ids = [ids]

        # don't allow turning on all relays
        # make duration required
        if ids is None or duration is None:
            return

        # make sure only one relay is enabled
        if len(ids) > 1:
            return

        # ensure all other relays are off
        self.disable()
        self._enable(ids, duration)
        self.emitter.emit("update", ids)

    def disable(self, ids: (str | list | None) = None):
        # normalize ids
        if isinstance(ids, str):
            ids = [ids]

        self._disable(ids)
        self.emitter.emit("update", ids)

    def cancel_timer(self, ids: (str | list | None) = None):
        # normalize ids
        if isinstance(ids, str):
            ids = [ids]

        self._cancel_timer(ids)
        self.emitter.emit("update", ids)

    def get_state(self, ids: (str | list | None) = None) -> list[dict[str, Any]]:
        # normalize ids
        if isinstance(ids, str):
            ids = [ids]

        return self._get_state(ids)

    def is_relay(self, id: str) -> bool:
        return id in self._relays

    def get_relay(self, id: str) -> RelayDevice:
        if not self.is_relay(id):
            raise KeyError(f"No relay with identifier: {id}")

        return self._relays[id]
