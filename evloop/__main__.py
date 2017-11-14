import sys
import time

from .loop import EventLoop, sleep


def main():

    def sync_fib(n):
        if n <= 1:
            return n
        else:
            a = sync_fib(n - 1)
            b = sync_fib(n - 2)
            return a + b

    def async_fib(n):
        if n <= 1:
            yield n
        else:
            a = yield async_fib(n - 1)
            b = yield async_fib(n - 2)
            yield a + b

    def read_input():
        while True:
            yield sys.stdin
            s = sys.stdin.readline().strip()
            print(s)
            n = int(s)
            fib_n = yield async_fib(n)
            print("{} fib({}) = {}".format(time.time(), n, fib_n))

    def interval(n):
        while True:
            print(time.time(), 'interval', n)
            yield from sleep(n)

    loop = EventLoop()
    loop.add_task(read_input())
    loop.add_task(interval(6))
    loop.add_task(interval(2))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.stop()


def server():
    from server.utils import create_server, close_socket, TEST_HTTP_RESPONSE

    def start_server():
        server = create_server()
        server.bind(('0.0.0.0', 8000))
        server.setblocking(False)
        server.listen()

        while True:
            sock = yield server
            conn, _ = sock.accept()
            conn.setblocking(False)
            conn = yield conn
            conn.recv(1024)
            conn.sendall(TEST_HTTP_RESPONSE)
            close_socket(conn)

    loop = EventLoop()
    loop.add_task(start_server())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.stop()


server()
