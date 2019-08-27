import threading
import tkinter

from gywer_matrix import GywerMatrixProtocol, GywerMatrix, UDPThreaded, UDPHandler

class GUI():
    def __init__(self, matrix, root):
        self.matrix = matrix
        self.root = root

    def run(self):
        pass



if __name__ == '__main__':
    ip, port = '0.0.0.0', 2390

    matrix = GywerMatrix(32, 32)
    protocol = GywerMatrixProtocol(matrix)
    server = UDPThreaded((ip, port), UDPHandler, protocol)

    root = tkinter.Tk()
    gui = GUI(matrix, root)

    server_thread = threading.Thread(target=server.serve_forever)

    # exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    gui_thread = threading.Thread(target=gui.run)
    gui_thread.daemon = True
    gui_thread.start()

    print('Server started.')

    try:
        root.mainloop()
        '''
        while True:
            pass
        '''
    except KeyboardInterrupt:
        pass

    server.shutdown()

    print('Server stoped.')
