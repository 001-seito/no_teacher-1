from asyncio.protocols import Protocol
from ev_command import EV, SPEED, INTERVAL, DIAMETER
import asyncio

r = 70  # default


def first_drive(transport):
    global ev
    ev = EV()
    while not ev.button.backspace:
        move_direction, color = ev.steer(r)
        transport.write("gyro:{}".format(str(move_direction)).encode())
        if color:
            transport.write("color:white")
        else:
            transport.write("color:black")

    ev.tank.off()
    transport.write("cmd:END_FIRST".encode())


class Client(Protocol):
    def connection_made(self, transport) -> None:
        print("Connected Into Server")
        self.transport = transport
        self.transport.write("speed:{}".format(SPEED).encode())
        self.transport.write("interval:{}".format(INTERVAL).encode())
        self.transport.write("diameter:{}".format(DIAMETER).encode())
        first_drive(transport)
        transport.write("cmd:START_SECOND".encode())

    def data_received(self, data) -> None:
        message = data.decode()
        (attr, data) = message.partition(':')
        global ev
        if attr == "direction":
            ev.turn_degrees(float(data))
        elif attr == "dist":
            ev.on_for_millis(float(data))


def main():
    loop = asyncio.get_event_loop()
    # ev = EV()

    c = loop.create_connection(Client)
    connection, addr = loop.run_until_complete(c)

    try:
        loop.run_forever()  # loop the tasks until the server is closed or ^C is sent
    except KeyboardInterrupt:
        pass

    loop.close()


if __name__ == '__main__':
    main()
