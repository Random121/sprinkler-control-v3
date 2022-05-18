from typing import Callable


# my python alternative for the nodejs EventEmitter
class EventEmitter:
    __events = {}

    @classmethod
    def subscribe(cls, event_name: str, listener: Callable) -> None:
        listener_list: list = cls.__events.setdefault(event_name, [])
        listener_list.append(listener)

    on = subscribe

    @classmethod
    def __once_wrap_listener(cls, event_name: str, listener: Callable) -> Callable:
        listener_info = {
            "called": False,
            # "wrapped_function": None,
        }

        def wrapped_function(*args, **kwargs):
            if not listener_info["called"]:
                listener_info["called"] = True
                cls.unsubscribe(event_name, wrapped_function)
                listener(*args, **kwargs)

        # listener_info["wrapped_function"] = wrapped_function

        return wrapped_function

    @classmethod
    def subscribe_once(cls, event_name: str, listener: Callable) -> None:
        cls.subscribe(event_name, cls.__once_wrap_listener(event_name, listener))

    once = subscribe_once

    @classmethod
    def unsubscribe(cls, event_name: str, listener: Callable) -> None:
        listener_list: list = cls.__events.get(event_name)
        if listener_list is not None:
            listener_list.remove(listener)
            # delete the entire list because nothing is there
            if len(listener_list) == 0:
                del cls.__events[event_name]

    off = unsubscribe

    @classmethod
    def emit(cls, event_name: str, *args, **kwargs) -> None:
        # make a clone of the list so we can iterate it while
        # modifying it (not the best idea)
        listener_list: list = list(cls.__events.get(event_name))
        if listener_list is not None:
            for listener in listener_list:
                listener(*args, **kwargs)


# emitter = EventEmitter()

# emitter.once("test", (lambda : print("ASD")))
# emitter.once("test", (lambda : print("ASD2")))
# emitter.subscribe("test", (lambda : print("ASD21")))

# emitter.emit("test")
