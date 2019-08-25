
import re
import socket


class GywerMatrixUDPServer(object):
    EFFECT_LIST = "Дыхание,Цвета,Снегопад,Шарик,Радуга,Радуга пикс,Огонь,The Matrix,Шарики,Часы,Звездопад,Конфетти,Радуга диагональная,Цветной шум,Облака,Лава,Плазма,Радужные переливы,Полосатые переливы,Зебра,Шумящий лес,Морской прибой,Лампа,Рассвет,Анимация 1,Анимация 2,Анимация 3,Анимация 4,Анимация 5"
    GAME_LIST = "Змейка,Тетрис,Лабиринт,Runner,Flappy Bird,Арканоид"
    ALARM_LIST = "Снегопад,Шарик,Радуга,Огонь,The Matrix,Шарики,Звездопад,Конфетти,Радуга диагональная,Цветной шум,Облака,Лава,Плазма,Радужные переливы,Полосатые переливы,Зебра,Шумящий лес,Морской прибой,Рассвет,Анимация 1,Анимация 2,Анимация 3,Анимация 4,Анимация 5"

    WIDTH = 16
    HEIGHT = 16
    BRIGHTNESS = 32

    """docstring for GywerMatrixUDPServer"""
    def __init__(self, local_port=2390, local_ip='0.0.0.0', buffer_size=1024):
        #super(GywerMatrixUDPServer, self).__init__()
        self.local_port = local_port
        self.local_ip = local_ip
        self.buffer_size  = buffer_size

        self.__acknowledge_counter = 0

        self.udp = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
        )
        self.udp.bind((self.local_ip, self.local_port))

        
        self.BTcontrol = True
        self.AUTOPLAY = True
        self.globalBrightness = self.BRIGHTNESS
        self.autoplayTime = 300
        self.idleTime = 6000
        self.isAlarmStopped = False
        self.useAutoBrightness = True
        self.autoBrightnessMin = 1

    def __upd_send_acknowledge(self, data):
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
                                self.WIDTH,
                                self.HEIGHT,
                                int(self.BTcontrol),
                                int(self.AUTOPLAY),
                                self.globalBrightness,
                                self.autoplayTime / 1000,
                                self.idleTime / 6000,
                                int(not self.isAlarmStopped),
                                int(self.useAutoBrightness),
                                self.autoBrightnessMin
                            )
            ),
            97: (lambda : 'LA:[{}]'.format(self.ALARM_LIST)),
            98: (lambda : 'LG:[{}]'.format(self.GAME_LIST)),
            99: (lambda : 'LE:[{}]'.format(self.EFFECT_LIST)),
        }
        try:
            reply = '$18 {};'.format(switcher[cmd]())
        except KeyError:
            self.__upd_send_acknowledge(data)
        else:
            self.udp.sendto(str.encode(reply), data[1])

    def parse(self, data):
        switcher = {
            18: {
                0: self.__upd_send_acknowledge,
                'else': self.__send_page_params,
            },

        }

        msg = data[0]

        #try
        message = msg.decode('utf-8') # ?
        #print(message)
        command = re.search(r'^\$([0-9]{1,2}) ?([0-9]{1,3}) ?([0-9]{1,2})?;$', message)
        print(command.group(1))
        print(command.group(2))

        cmd = int(command.group(1))
        subcmd = int(command.group(2))

        if cmd in switcher:
            if int(subcmd) in switcher[cmd]:
                switcher[cmd][subcmd](data)
            else:
                switcher[cmd]['else'](data, subcmd)




    def run(self):
        while(True):
            recieved = self.udp.recvfrom(self.buffer_size)
            print('Message from Client:{} \n'
                  'Client IP Address:{}'.format(recieved[0],recieved[1]))
            self.parse(recieved)



if __name__ == '__main__':
    server = GywerMatrixUDPServer()
    try:
        server.run()
    except KeyboardInterrupt:
        pass

