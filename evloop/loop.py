import selectors
import time
import types
from collections import deque
from functools import partial


class EventLoop:

    def __init__(self, sleep_time=None, selector=None):
        self._running = False
        self._sleep_time = sleep_time
        self._tasks = deque()
        if not selector:
            selector = selectors.DefaultSelector()
        self._selector = selector

    def add_task(self, coro, value=None, parents=None):
        if isinstance(coro, types.GeneratorType) or str(type(coro)) == "<class 'generator'>":
            task = partial(self._handle, coro, value, parents)
            self._tasks.append(task)
        else:
            raise Exception('coro must be a generator')

    def run_forever(self):
        self._running = True
        while self._running:
            if self._tasks:
                task = self._tasks.popleft()
                task()
            if self._sleep_time is not None:
                time.sleep(self._sleep_time)
        self._running = False

    def stop(self):
        self._running = False

    def _handle(self, coro, value=None, parents=None):
        if parents is None:
            parents = deque()
        try:
            if self._is_fileobj(value):
                expected = value
                if self._pop_ready_key(value):
                    expected = coro.send(value)
            else:
                expected = coro.send(value)
        except StopIteration:
            if parents:
                parent_task = parents.pop()
                self.add_task(parent_task, value, parents)
        else:
            if isinstance(expected, types.GeneratorType):
                parents.append(coro)
                self.add_task(expected, parents=parents)
            else:
                if self._is_fileobj(expected):
                    try:
                        self._selector.register(expected, selectors.EVENT_READ)
                    except KeyError:
                        pass
                self.add_task(coro, expected, parents)

    @staticmethod
    def _is_fileobj(value):
        return hasattr(value, 'fileno')

    def _pop_ready_key(self, fileobj):
        for key, _ in self._selector.select(0):
            if key.fileobj is fileobj:
                self._selector.unregister(fileobj)
                return key
        return None


def sleep(timeout):
    start = time.time()
    while True:
        yield
        if time.time() >= start + timeout:
            break
