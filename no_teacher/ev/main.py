from math import degrees
from ev_command import EV
from time import sleep
import socket

r = 70  # default


def first_drive(ev, s):
    while not ev.button.backspace:
        ev.steer(s, r)
    ev.tank.off()
    s.send('END')


def second_drive(ev, s):
    while True:
        direction = s.recv(1024).decode()
        dist = s.recv(1024).decode()
        ev.tank.turn_degrees(degrees(direction))
        ev.tank.on_for_seconds(dist)


def main():
    ev = EV()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('xxxx', XXXX))  # IP
    except:
        print("failed to connect with PC in BlueTooth")
        exit(1)

    first_drive(ev, s)
    # 何周かしてるうちにどれだけ誤差を少なく座標をプロットできるか
    # 1周でも十分では

    flag = False
    while True:
        if 'Shall I go?' == s.recv(1024).decode():
            flag = True
        if ev.button.up and flag:
            break
    # 手動でスタート位置まで戻して upボタン、2回目の走行
    s.send('Go ahead'.encode())
    second_drive(ev, s)


if __name__ == '__main__':
    main()
