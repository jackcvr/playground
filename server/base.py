import selectors
import socket
from functools import partial

from .utils import create_server


class TCPServer:
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    reuse_address = True

    def __init__(self, address, handler=None, selector=None):
        from .handlers import RequestHandler

        self._socket = create_server(
            address_family=self.address_family,
            socket_type=self.socket_type,
            reuse_address=self.reuse_address,
        )
        self._socket.bind(address)
        self.address = self._socket.getsockname()
        self._socket.setblocking(False)

        if handler is None:
            handler = RequestHandler
        self._handler = handler

        if selector is None:
            selector = selectors.DefaultSelector()
        self._selector = selector

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def stop(self):
        self._selector.close()
        self._socket.close()

    def start(self, timeout=0.5):
        self._socket.listen()
        self._selector.register(self._socket, selectors.EVENT_READ, self._accept)

        while True:
            for key, _ in self._selector.select(timeout):
                try:
                    key.data()
                except TypeError:
                    raise Exception('Registered event data must be a callable object.')

    def _accept(self):
        conn, addr = self._socket.accept()
        handler = partial(self._run_handler, self._handler, conn, addr)
        self._selector.register(conn, selectors.EVENT_READ, handler)

    def _run_handler(self, handler, sock, addr):
        self._selector.unregister(sock)
        handler(sock, addr)
