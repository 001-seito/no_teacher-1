from ev_command import EV, SPEED, INTERVAL, DIAMETER
import asyncio

r = 50

def first_drive(writer, ev):
    while not ev.button.up:
        move_direction, color = ev.steer(r)
        writer.write("gyro:{}".format(str(move_direction)).encode())
        if color:
            writer.write("color:white".encode())
        else:
            writer.write("color:black".encode())

    ev.tank.off()
    writer.write("cmd:END_FIRST".encode())

def second_drive(ev, reader):
    while True:
        message = yield from reader.read(1 << 15)
        (attr, _, data) = message.decode().partition(':')
        print(data)
        if attr == "direction":
            ev.turn_degrees(float(data))
        elif attr == "dist":
            ev.on_for_millis(float(data))

def client(loop, ev):
    _, writer = yield from asyncio.open_connection('169.254.225.141', 50010, loop=loop)
    print("Connected into server")

    data1 = "values:{} {} {}".format(SPEED, INTERVAL, DIAMETER).encode()
    writer.write(data1)

    print("Starting 1st drive")
    first_drive(writer, ev)

    reader, writer = yield from asyncio.open_connection('169.254.225.141', 50010, loop=loop)
    print("Connected into server")

    writer.write("cmd:START_SECOND".encode())
    print("Starting 2nd drive")
    second_drive(ev, reader)

def main():
    loop = asyncio.get_event_loop()
    ev = EV()

    loop.run_until_complete(client(loop, ev))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
        exit(1)
    loop.close()

if __name__ == '__main__':
    main()
