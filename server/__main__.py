from concurrent.futures import ProcessPoolExecutor

from .base import TCPServer
from .handlers import HTTPRequestHandler


def main(address, processes=None):
    server = TCPServer(
        address,
        handler=HTTPRequestHandler(executor=ProcessPoolExecutor(processes)),
    )
    with server:
        server.start()


main(('0.0.0.0', 8000))
