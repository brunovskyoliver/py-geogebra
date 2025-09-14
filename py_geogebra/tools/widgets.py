from typing import Callable


class Widgets:
    def __init__(self):
        self._registry = []

    def register(
        self, update_func: Callable[[], None]
    ):  # https://docs.python.org/3/library/typing.html#annotating-callable-objects
        self._registry.append(update_func)
        update_func()

    def refresh(self):
        for update_func in self._registry:
            update_func()
