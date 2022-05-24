from typing import Callable


# my python alternative for the nodejs EventEmitter
class EventEmitter:
    def __init__(self) -> None:
        self._events = {}

    def add_listener(self, event: str, listener: Callable):
        listeners: list = self._events.setdefault(event, [])
        listeners.append(listener)

    on = add_listener

    def remove_listener(self, event: str, listener: Callable):
        listeners: list = self._events.get(event)
        if listeners:
            listeners.remove(listener)
            # NOTE: can be uncommented for memory optimization
            # if len(listeners) == 0:
            #     del self._events[event]

    off = remove_listener

    # NOTE: internal method and should not be public
    def __create_once_wrapper(self, event: str, listener: Callable):
        function_called: bool = False

        def wrapped_listener(*args, **kwargs):
            nonlocal function_called
            if not function_called:
                function_called = True
                self.remove_listener(event, wrapped_listener)
                listener(*args, **kwargs)

        return wrapped_listener

    def add_once_listener(self, event: str, listener: Callable):
        self.add_listener(event, self.__create_once_wrapper(event, listener))

    once = add_once_listener

    def emit(self, event: str, *args, **kwargs):
        # make a clone of the list so it can be iterated while being modified
        # TODO: find a better way of doing this
        listeners: list = list(self._events.get(event))
        if listeners:
            for listener in listeners:
                listener(*args, **kwargs)