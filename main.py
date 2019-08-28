import threading
import tkinter
import time

from gywer_matrix import GywerMatrixProtocol, GywerMatrix, UDPThreaded, UDPHandler

class GUI():
    def __init__(self, matrix, root, cell_size=16):
        self.matrix = matrix
        self.root = root
        self.cell_size = cell_size

        self.root.title('GywerMatrix WiFi')
        width = self.matrix.width * self.cell_size
        height = self.matrix.height * self.cell_size
        self.root.minsize(width=width, height=height)
        self.canvas = tkinter.Canvas(self.root, width=width, height=height)
        self.canvas.pack()


    def run(self):
        while True:
            mx = 0
            for column in self.matrix.matrix:
                my = self.matrix.height - 1
                for cell in column:
                    x = mx * self.cell_size
                    y = my * self.cell_size

                    self.canvas.create_rectangle(x, y,
                                     x+self.cell_size, y + self.cell_size,
                                     fill='#{:06x}'.format(cell))
                    my = my -1
                mx += 1

            #time.sleep(1/20)
            self.matrix.updated.wait()


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
