import socket
import math
from time import sleep

from ev3dev2.motor import SpeedRPS

# from no_teacher.consts import SPEED, INTERVAL
SPEED = SpeedRPS(1.0)
INTERVAL = 200
DIAMETER = 55  # milli meter


def init():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', XXXX))
    s.listen(1)
    return s


def recv_first_drive_data(socket):
    # n == 6乗ぐらい？
    data = []
    while True:
        connect, _ = socket.accept()
        with connect:
            while True:
                direction = connect.recv(1024).decode()
                if direction == 'END':
                    return data
                elif not direction:
                    break
                else:
                    data.append(float(direction))


def data_to_position(data):
    position = [(0.0, 0.0)]
    x = 0
    y = 0
    delta = SPEED * (INTERVAL / 1000) * DIAMETER * 2 * math.pi
    for d in data:
        radian = math.radians(d)
        dx = delta * math.cos(radian)
        dy = delta * math.sin(radian)
        x += dx
        y += dy
        position.append((x, y))
    position

# あとはこれを numpy matplot に渡して描画


def serve_second_drive(socket, position):
    current_direction = 0.0
    bx = 0
    by = 0
    for (cx, cy) in position:
        new_direction = math.atan2(cy, cx)
        distance = math.sqrt((cx - bx) ** 2 + (cy - by) ** 2)
        turn_radian = new_direction - current_direction
        socket.send(str(turn_radian).encode())
        socket.send(str(distance).encode())
        bx = cx
        by = cy


def main():
    socket = init()
    data = recv_first_drive_data(socket)
    position = data_to_position(data)

    # plot
    while True:
        socket.send('Shall I go?'.encode())
        sleep(0.2)
        if 'Go ahead' == socket.recv(1024).decode():
            break
    serve_second_drive(socket, position)


if __name__ == '__main__':
    main()

