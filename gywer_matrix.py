import re
import socket
#import tkinter


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

        self.__matrix = [
            [0 for x in range(self.__width)] for y in range(self.__height)
        ]

    def draw_pixel_xy(self, x, y, color):
        print('draw x:{} y:{} color:{}'.format(x,y,color))
        if (x >= 0) and (x < self.__width) and (y >= 0) and (y < self.__height):
            self.__matrix[x][y] = color
        else:
            raise ValueError('Out of matrix range.')

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


        
class GywerMatrixUDPServer(object):
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


    """docstring for GywerMatrixUDPServer"""
    def __init__(self, matrix_object=GywerMatrix(), local_port=2390,
                 local_ip='0.0.0.0', buffer_size=1024):
        super(GywerMatrixUDPServer, self).__init__()

        self.local_port = local_port
        self.local_ip = local_ip
        self.buffer_size = buffer_size

        self.matrix = matrix_object
        self.__acknowledge_counter = 0

        self.udp = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
        )
        self.udp.bind((self.local_ip, self.local_port))
       
    def __upd_send_acknowledge(self, data, cmd):
        print('ack')
        reply = 'ack {:d};'.format(self.__acknowledge_counter)
        self.__acknowledge_counter += 1
        self.udp.sendto(str.encode(reply), data[1])

    def __send_page_params(self, data, cmd):

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
            self.__upd_send_acknowledge(data)
        else:
            self.udp.sendto(str.encode(reply), data[1])

    def __set_brightnest(self, data, cmd):
        if cmd[0] == 0:
            self.matrix.global_brightness = cmd[1]
        elif cmd[0] == 1:
            self.matrix.auto_brightness = cmd[1]
            self.matrix.auto_brightness_minimal = cmd[2]

    def __draw(self, data, cmd):
        self.matrix.manual_control = True
        self.matrix.drawing_flag = True
        self.matrix.running_flag = False

        #game mode!
        #color effect!

        #gamma_correction!
        self.matrix.draw_pixel_xy(cmd[0], cmd[1], self.matrix.global_color)

    def __set_global_color(self, data, cmd):
        self.matrix.global_color = cmd[0]


    def parse(self, data):
        switcher = {
            0: self.__set_global_color,
            1: self.__draw,
            4: self.__set_brightnest,
            18: {
                0: self.__upd_send_acknowledge,
                'else': self.__send_page_params,
            },

        }

        msg = data[0]

        # try
        message = msg.decode('utf-8') # ?
        # print(message)
        command = re.search(r'^\$([0-9a-fA-F\. ]+);$', message)
        print(command.group(1))

        #cmd = [int(x) for x in command.group(1).split()]
        cmd = []
        for x in command.group(1).split():
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
                    switcher[cmd[0]][cmd[1]](data, cmd[1:])
                elif 'else' in switcher[cmd[0]]:
                    switcher[cmd[0]]['else'](data, cmd[1:])
            except TypeError:
                switcher[cmd[0]](data, cmd[1:])


    def run(self):
        while(True):
            recieved = self.udp.recvfrom(self.buffer_size)
            print('Message from Client:{} \n'
                  'Client IP Address:{}'.format(recieved[0],recieved[1]))
            self.parse(recieved)