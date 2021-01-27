import asyncio
from time import sleep
import math
import matplotlib.pyplot as plt
import random

TEST_ID = random.randint(0, 1 << 16)

def convert_data(gyro_data, motor_speed, interval, diameter, colors):
    step = diameter * math.pi * motor_speed * interval / 1000
    cx = 0.0
    cy = 0.0

    positions = [(0.0, 0.0, True)]

    for (degree, color) in zip(gyro_data, colors):
        dx = step * math.cos(math.radians(degree))
        dy = step * math.sin(math.radians(degree))
        cx += dx
        cy += dy
        positions.append((cx, cy, color == "black"))
        print(cx, cy)
        plt.plot(cx, cy, '-',)

    plt.savefig("course_first_drive@{}.png".format(TEST_ID))

    return positions


class Server(asyncio.Protocol):
    gyro_data = []
    colors = []
    motor_speed = 100
    interval = 100
    diameter = 55

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        (attr, _, data) = message.partition(':')
        if attr == "gyro":
            f = float(data)
            print(f)
            self.gyro_data.append(f)
        elif attr == "color":
            print(data)
            self.colors.append(data)
        elif attr == "cmd" and data == "END_FIRST":
            print("Close the connect")
            self.transport.close()

        elif attr == "cmd" and data == "START_SECOND":
            positions = convert_data(self.gyro_data, self.motor_speed,
                                     self.interval,  self.diameter, self.colors)
            print("converted data")
            black_points = []
            for (x, y, c) in positions:
                if c:
                    black_points.append((x, y))

            current_direction = 0.0
            for i in range(len(black_points) - 1):
                (bx, by) = black_points[i]
                (cx, cy) = black_points[i + 1]
                next_direction = math.degrees(
                    math.atan2((cy - by), (cx - bx)))
                turn_direction = next_direction - current_direction
                distance = math.sqrt((cx - bx) ** 2 + (cy - by) ** 2)
                print(turn_direction, distance)
                self.transport.write(
                    "direction:{}".format(turn_direction).encode())
                sleep(0.2)
                self.transport.write("dist:{}".format(distance).encode())
                sleep(0.2)
                current_direction = next_direction


def main():
    loop = asyncio.get_event_loop()
    s = loop.create_server(Server, '169.254.225.141', 50010)  # ip, port
    server = loop.run_until_complete(s)  # starting server blocking
    print('Serving on {}'.format(server.sockets[0].getsockname()))

    try:
        loop.run_forever()  # loop the tasks until the server is closed or ^C is sent
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    print("Server succesfully closed")
    loop.close()


if __name__ == '__main__':
    main()
