from ev_command import EV, SPEED, INTERVAL, DIAMETER
import asyncio

r = 70

def first_drive(writer, ev):
    while not ev.button.backspace:
        move_direction, color = ev.steer(r)
        writer.write("gyro:{}".format(str(move_direction)).encode())
        if color:
            writer.write("color:white")
        else:
            writer.write("color:black")

    ev.tank.off()
    writer.write("cmd:END_FIRST".encode())


def second_drive(ev, reader):
    while True:
        message = yield reader.read(1024)
        (attr, data) = message.decode().partition(':')
        if attr == "direction":
            ev.turn_degrees(float(data))
        elif attr == "dist":
            ev.on_for_millis(float(data))


def client(loop, ev):
    reader, writer = yield asyncio.open_connection('169.127.0.0', 50010, loop=loop)
    print("Connected Into Server")

    writer.write("speed:{}".format(SPEED).encode())
    writer.write("interval:{}".format(INTERVAL).encode())
    writer.write("diameter:{}".format(DIAMETER).encode())

    first_drive(writer, ev)

    writer.write("cmd:START_SECOND".encode())

    second_drive(ev, reader)


def main():
    loop = asyncio.get_event_loop()
    ev = EV()

    loop.run_until_complete(client(loop, ev))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    loop.close()


if __name__ == '__main__':
    main()
