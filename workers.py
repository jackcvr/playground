import multiprocessing as mp
import threading


class QueueMixin:

    def __init__(self, *args, **kwargs):
        self._input = kwargs.pop('input')
        self._output = kwargs.pop('output', None)
        self._is_running = True
        super().__init__(*args, **kwargs)

    def run(self):
        while self._is_running:
            item = self._get()
            if item is None:
                break
            result = self._handle(item)
            if self._output and result:
                self._output.put_nowait(result)

    def stop(self):
        self._is_running = False
        self._put(None)

    def _get(self):
        return self._input.get()

    def _put(self, item):
        self._input.put_nowait(item)

    def _handle(self, item):
        pass


class ThreadWorker(QueueMixin, threading.Thread):
    pass


class ProcessWorker(QueueMixin, mp.Process):
    pass
