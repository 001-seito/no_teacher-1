from ev3dev2.motor import Motor, MoveSteering, OUTPUT_B, OUTPUT_C, SpeedPercent, SpeedRPS
from ev3dev2.sensor.lego import ColorSensor, GyroSensor
from ev3dev2.button import Button

import math
import socket
from time import sleep

# from no_teacher.consts import SPEED, INTERVAL
SPEED = SpeedRPS(1.0)
INTERVAL = 200
DIAMETER = 55  # milli meter


class EV:

    def __init__(self):
        self.button = Button()

        self.tank = MoveSteering(OUTPUT_C, OUTPUT_B)

        self.cs = ColorSensor()
        self.cs.mode = ColorSensor.MODE_COL_REFLECT

        self.gs = GyroSensor()
        self.gs.reset()
        self.before_direction = self.gyro()

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('xxxx', XXXX))  # IP
        except:
            print("failed to connect with PC in BlueTooth")
            exit(1)

    def steer(self, steer, speed=SPEED, interval=INTERVAL):
        """
        steer the motor by given params for time intarval [ms]
        """
        if self.is_white():  # clockwise
            self.tank.on_for_seconds(steer, speed, interval / 1000)
        else:
            self.tank.on_for_seconds(-steer, speed, interval / 1000)

        data = self._update_direction()
        self._send(data)

        sleep(interval / 1000)

    def turn_degrees(self, radian):
        self.tank.turn_degrees(SPEED, radian * 360 / (2 * math.pi))

    def on_for_millis(self, millis):
        self.tank.on_for_seconds(0, SPEED, millis / 1000)

    def gyro(self):
        return self.gs.value()

    def is_white(self):
        return self.cs.value() > 30

    def _send(self, data):
        data = str(data).encode()
        self.socket.send(data)
        print(data)

    def _update_direction(self):
        current_direction = self.gyro()
        m_direction = (current_direction + self.before_direction) / 2
        self.before_direction = current_direction
        return m_direction
