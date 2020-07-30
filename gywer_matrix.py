import re
import socket
import socketserver
import threading


class GywerMatrix(object):
    """docstring for GywerMatrix"""

    BRIGHTNESS = 32
    BRIGHTNESS_MIN = 0
    BRIGHTNESS_MAX = 256 #?

    
    def __init__(self, width=16, height=16):
        super(GywerMatrix, self).__init__()

        self.__width = width
        self.__height = height
        self.__manual_control = True
        self.__auto_play = True
        self.__global_brightness = self.BRIGHTNESS
        self.__auto_brightness = True #?
        self.__auto_brightness_minimal = 1 #?
        self.__auto_play_time = 6000 #?
        self.__idle_time = 6000 #?
        self.__global_color = 0xFFFFFF
        self.__drawing_flag = False
        self.__running_flag = False #?

        self.updated = threading.Event()

        self.clear()

    def draw_pixel_xy(self, x, y, color):
        print('draw x:{} y:{} color:{}'.format(x,y,color))
        if (x >= 0) and (x < self.__width) and (y >= 0) and (y < self.__height):
            self.__matrix[x][y] = color
            self.updated.set()
        else:
            raise ValueError('Out of matrix range.')

    def clear(self):
        self.__matrix = [
            [0 for x in range(self.__width)] for y in range(self.__height)
        ]
        self.updated.set()

    @property
    def matrix(self):
        return self.__matrix

    @property
    def auto_play_time(self):
        return self.__auto_play_time

    @auto_play_time.setter
    def auto_play_time(self, value):
        if value >= 0 :
            self.__auto_play_time = value
        else:
            raise ValueError('Value must be positive.')

    @property
    def drawing_flag(self):
        return self.__drawing_flag

    @drawing_flag.setter
    def drawing_flag(self, value):
        self.__drawing_flag = bool(value)

    @property
    def running_flag(self):
        return self.__running_flag

    @running_flag.setter
    def running_flag(self, value):
        self.__running_flag = bool(value)

    @property
    def idle_time(self):
        return self.__idle_time
    
    @idle_time.setter
    def idle_time(self, value):
        if value >= 0:
            self.__idle_time = value
        else:
            raise ValueError('Value must be positive.')
    
    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def global_color(self):
        return self.__global_color

    @global_color.setter
    def global_color(self, value):
        self.__global_color = value
    

    @property
    def manual_control(self):
        return self.__manual_control

    @manual_control.setter
    def manual_control(self, value):
        self.__manual_control = bool(value)

    @property
    def auto_play(self):
        return self.__auto_play
    
    @auto_play.setter
    def auto_play(self, value):
        self.__auto_play = bool(value)

    def __check_brightness(self, value):
        value = int(value)
        if (value > self.BRIGHTNESS_MIN) and (value < self.BRIGHTNESS_MAX):
            return value
        else:
            raise ValueError('Value is out of range. ({},{})'.format(self.BRIGHTNESS_MIN,
                                                               self.BRIGHTNESS_MAX))

    @property
    def global_brightness(self):
        return self.__global_brightness

 
    @global_brightness.setter
    def global_brightness(self, value):
        print(value)
        self.__global_brightness = self.__check_brightness(value)
        

    @property
    def auto_brightness(self):
        return self.__auto_brightness
    
    @auto_brightness.setter
    def auto_brightness(self, value):
        self.__auto_brightness = bool(value)

    @property
    def auto_brightness_minimal(self):
        return self.__auto_brightness_minimal

    @auto_brightness_minimal.setter
    def auto_brightness_minimal(self, value):
        self.__auto_brightness_minimal = self.__check_brightness(value)


        
class GywerMatrixProtocol(object):
    EFFECT_LIST = "Дыхание,Цвета,Снегопад,Шарик,Радуга,Радуга пикс,Огонь,\
                  The Matrix,Шарики,Часы,Звездопад,Конфетти,Радуга \
                  диагональная,Цветной шум,Облака,Лава,Плазма,Радужные \
                  переливы,Полосатые переливы,Зебра,Шумящий лес,Морской \
                  прибой,Лампа,Рассвет,Анимация 1,Анимация 2,Анимация 3,\
                  Анимация 4,Анимация 5"

    GAME_LIST = "Змейка,Тетрис,Лабиринт,Runner,Flappy Bird,Арканоид"

    ALARM_LIST = "Снегопад,Шарик,Радуга,Огонь,The Matrix,Шарики,Звездопад,\
                 Конфетти,Радуга диагональная,Цветной шум,Облака,Лава,Плазма,\
                 Радужные переливы,Полосатые переливы,Зебра,Шумящий лес,\
                 Морской прибой,Рассвет,Анимация 1,Анимация 2,Анимация 3,\
                 Анимация 4,Анимация 5"

    def __init__(self, matrix_object=GywerMatrix()):
        super(GywerMatrixProtocol, self).__init__()

        self.matrix = matrix_object
        self.__acknowledge_counter = 0

    def __send_acknowledge(self, cmd=None):
        reply = 'ack {:d};'.format(self.__acknowledge_counter)
        self.__acknowledge_counter += 1
        return reply

    def __send_page_params(self, cmd):

        print('__send_page_params')
        switcher = {
            1: (
                lambda: 'W:{}|H:{}|DM:{}|AP:{}|BR:{}'
                        '|PD:{}|IT:{}|AL:{}'
                        '|BU:{}|BY:{}'.format(
                                self.matrix.width,
                                self.matrix.height,
                                int(self.matrix.manual_control),
                                int(self.matrix.auto_play),
                                self.matrix.global_brightness,
                                self.matrix.auto_play_time / 1000,
                                self.matrix.idle_time / 6000,
                                False, #int(not self.isAlarmStopped),
                                int(self.matrix.auto_brightness),
                                self.matrix.auto_brightness_minimal
                            )
            ),
            2: (
                lambda: 'BR:{}|CL:{:06x}|BU:{}|BY:{}'.format(
                        self.matrix.global_brightness,
                        self.matrix.global_color,
                        int(self.matrix.auto_brightness),
                        self.matrix.auto_brightness_minimal
                    )
            ),
            97: (lambda: 'LA:[{}]'.format(self.ALARM_LIST)),
            98: (lambda: 'LG:[{}]'.format(self.GAME_LIST)),
            99: (lambda: 'LE:[{}]'.format(self.EFFECT_LIST)),
        }
        try:
            reply = '$18 {};'.format(switcher[cmd[0]]())
        except KeyError:
            self.__send_acknowledge()
        else:
            return reply

    def __set_brightnest(self, cmd):
        if cmd[0] == 0:
            self.matrix.global_brightness = cmd[1]
        elif cmd[0] == 1:
            self.matrix.auto_brightness = cmd[1]
            self.matrix.auto_brightness_minimal = cmd[2]

    def __draw(self, cmd):
        self.matrix.manual_control = True
        self.matrix.drawing_flag = True
        self.matrix.running_flag = False

        #game mode!
        #color effect!

        #gamma_correction!
        self.matrix.draw_pixel_xy(cmd[0], cmd[1], self.matrix.global_color)

    def __set_global_color(self, cmd):
        self.matrix.global_color = cmd[0]

    def __receive_image(self, cmd):
        self.matrix.manual_control = True
        self.matrix.running_flag = False

        if not self.matrix.drawing_flag:
            self.matrix.clear()
            self.matrix.drawing_flag = True

        y = cmd[0]
        row = list(zip(cmd[1::2], cmd[2::2]))

        for color, x in row:
            if (x == 0) and (y == 0):
                self.matrix.clear()

            self.matrix.draw_pixel_xy(x, self.matrix.height-y-1, color)
            last_x = x
        reply = '$5 {1}-{0} {2}'.format(x, y, self.__send_acknowledge())
        print(reply)
        return reply

    def parse(self, message):
        switcher = {
            0: self.__set_global_color,
            1: self.__draw,
            4: self.__set_brightnest,
            5: self.__receive_image,
            18: {
                0: self.__send_acknowledge,
                'else': self.__send_page_params,
            },

        }

        print(message)
        full_command = re.search(r'^\$([0-9a-fA-F\. ]+);$', message)
        command_begin = re.search(r'^\$([0-9a-fA-F\.| ]+)$', message)
        command_middle = re.search(r'^([0-9a-fA-F\.| ]+)$', message)
        command_end = re.search(r'^([0-9a-fA-F\.| ]+);$', message)

        command = full_command or command_begin

        command = command.group(1)

        print(command)


        command = command.replace('|', ' ')
        command = command.split()

        cmd = []
        for x in command:
            try:
                cmd.append(int(x))
            except ValueError:
                try:
                    cmd.append(int(x, 16))
                except ValueError:
                    pass
                else:
                    continue

            else:
                continue

            cmd.append(float(x))



        if cmd[0] in switcher:
            try:
                if cmd[1] in switcher[cmd[0]]:
                    return switcher[cmd[0]][cmd[1]](cmd[1:])
                elif 'else' in switcher[cmd[0]]:
                    return switcher[cmd[0]]['else'](cmd[1:])
            except TypeError:
                return switcher[cmd[0]](cmd[1:])


class UDPThreaded(socketserver.ThreadingMixIn, socketserver.UDPServer):
    def __init__(self, server_address, RequestHandlerClass, protocol):
        socketserver.UDPServer.__init__(self, server_address, RequestHandlerClass)
        self.protocol = protocol


class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        reply = self.server.protocol.parse(data.decode('utf-8'))
        if reply:
            socket.sendto(reply.encode(), self.client_address)

