import threading

from gywer_matrix import GywerMatrixProtocol, GywerMatrix, UDPThreaded, UDPHandler


if __name__ == '__main__':
    ip, port = '0.0.0.0', 2390

    protocol = GywerMatrixProtocol(GywerMatrix(32, 32))
    server = UDPThreaded((ip, port), UDPHandler, protocol)

    server_thread = threading.Thread(target=server.serve_forever)

    # exit the server thread when the main thread terminates
    server_thread.daemon = True

    server_thread.start()

    print('Server started.')
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

    server.shutdown()
    print('Server stoped.')
