import asyncio
import math
import numpy
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
        plt.plot(cx, cy, '-', color=str(color == "black"), m='o')

    plt.savefig("course_first_drive@{}.png".format(TEST_ID))

    return positions


class Server(asyncio.Protocol):
    phase = 1
    gyro_data = []
    colors = []
    # motor_speed = None
    # interval = None
    # diameter = None

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        (attr, data) = message.partition(':')
        if self.phase == 0:  # initialize state
            if attr == "speed":
                self.motor_speed = float(data)
            if attr == "interval":
                self.interval = float(data)
            if attr == "diameter":
                self.diameter = float(data)
            if self.motor_speed != None and self.interval != None and self.diameter != None:
                self.phase = 1
        elif self.phase == 1:  # recv first_drive data
            if attr == "gyro":
                f = float(data)
                self.gyro_data.append(f)
            if attr == "color":
                self.colors.append(data)
            if attr == "cmd" and data == "END_FIRST":
                self.phase = 2
        elif self.phase == 2:  # serve the second_drive data
            if attr == "cmd" and data == "START_SECOND":
                positions = convert_data(self.gyro_data, self.motor_speed,
                                         self.interval,  self.diameter, self.colors)
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
                    self.transport.write("direction:{}".format(turn_direction))
                    self.transport.write("dist:{}".format(distance))
                    current_direction = next_direction


def main():
    loop = asyncio.get_event_loop()
    s = loop.create_server(Server, '127.0.0.1', 50010)  # ip, port
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
