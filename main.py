
from gywer_matrix import GywerMatrixUDPServer, GywerMatrix


if __name__ == '__main__':
    server = GywerMatrixUDPServer(GywerMatrix(32, 32))
    try:
        server.run()
    except KeyboardInterrupt:
        pass
