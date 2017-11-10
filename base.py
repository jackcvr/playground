import socket


TEST_HTTP_RESPONSE = b'HTTP/1.1 200 OK\n\ntest\n'


def create_server(address_family=socket.AF_INET, socket_type=socket.SOCK_STREAM, reuse_address=True):
    server = socket.socket(address_family, socket_type)
    if reuse_address:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return server


def close_socket(sock):
    try:
        sock.shutdown(socket.SHUT_WR)
    except OSError:
        pass
    sock.close()


def main(address, **kwargs):
    server = create_server(**kwargs)
    server.bind(address)
    server.listen()

    while True:
        conn, _ = server.accept()
        conn.recv(1024)
        conn.sendall(TEST_HTTP_RESPONSE)
        close_socket(conn)


if __name__ == '__main__':
    main(('0.0.0.0', 8000))
