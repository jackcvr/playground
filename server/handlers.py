import copy
import logging

from .utils import TEST_HTTP_RESPONSE, close_socket


class RequestHandler:
    R_BUFSIZE = -1
    W_BUFSIZE = 0

    def __init__(self, executor=None, logger=None):
        self._executor = executor
        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger

    def __getstate__(self):
        state = self.__dict__.copy()
        if '_executor' in state:
            del state['_executor']
        return state

    def __call__(self, sock, addr):
        self._socket = sock
        self._addr = addr

        if self._executor:
            handler = copy.copy(self)  # for saving socket state
            future = self._executor.submit(handler.handle)
            future.add_done_callback(handler._close)
        else:
            try:
                self.handle()
            except Exception as e:
                self._handle_error(e)
            finally:
                self._close()

    def handle(self):
        try:
            data_dict = self._read_request()
            response = self._get_response(**data_dict)
            if not isinstance(response, bytes):
                response = response.encode('utf-8')
            self._socket.sendall(response)
        finally:
            self._close()

    def _read_request(self):
        return {'body': self._socket.recv(1024)}

    def _get_response(self, **kwargs):
        return repr(kwargs)

    def _close(self, future=None):
        if future:
            e = future.exception()
            if e:
                self._handle_error(e)
        close_socket(self._socket)

    def _handle_error(self, e):
        self.logger.error(repr(e))


class HTTPRequestHandler(RequestHandler):

    def _read_request(self):
        rfile = self._socket.makefile('rb', self.R_BUFSIZE)
        lines = []
        while True:
            line = rfile.readline().decode('utf-8')
            if line in ('\r\n', '\n', ''):
                break
            lines.append(line.rstrip('\r\n'))
        rfile.close()
        if lines:
            try:
                method, path, version = lines[0].split()
                return {
                    'method': method,
                    'path': path,
                    'version': version,
                    'headers': {h[0]: h[1] for h in (l.split(':') for l in lines[1:])},
                }
            except IndexError:
                pass
        return {}

    def _get_response(self, method=None, path=None, headers=None, **kwargs):
        if not method:
            return 'HTTP/1.1 400 Bad Request\n'
        return TEST_HTTP_RESPONSE
