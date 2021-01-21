from math import degrees
from ev_command import EV
from time import sleep

r = 70 # default

def first_drive(ev):
    while not ev.button.backspace:
        ev.steer(r)
    ev.tank.off()
    ev._send('END')

def second_drive(ev):
    while True:
        direction = ev.socket.recv(1024).decode()
        dist = ev.socket.recv(1024).decode()
        ev.tank.turn_degrees(degrees(direction))
        ev.tank.on_for_seconds(dist)


def main():
    ev = EV()
    first_drive(ev)
    # 何周かしてるうちにどれだけ誤差を少なく座標をプロットできるか
    # 1周でも十分では

    flag = False
    while True:
        if 'Shall I go?' == ev.socket.recv(1024).decode():
            flag = True
        if ev.button.up and flag:
            break
    # 手動でスタート位置まで戻して upボタン、2回目の走行
    ev.socket.send('Go ahead'.encode())
    second_drive(ev)

if __name__ == '__main__':
    main()
