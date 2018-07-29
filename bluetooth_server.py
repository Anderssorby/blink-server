#!/usr/bin/env python
from multiprocessing import Process

import bluetooth
import core


def main():
    # BLUETOOTH SECTION
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    bluetooth.advertise_service(
        server_sock,
        "sinkServer",
        service_id=uuid,
        service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE])

    print("READY FOR CONNECTIONS, RFCOMM channel %d" % port)

    while True:
        client_sock, client_info = server_sock.accept()
        print("INBOUND CONNECTION ", client_info)
        try:
            while True:
                data = client_sock.recv(1024).decode("utf-8")
                if not data:
                    break

                print("COMMAND RECEIVED [%s]" % data)
                if data == "marco":
                    client_sock.send("polo\n")
                else:
                    process = Process(target=core.commandKeys, args=(data,))
                    process.start()
        except IOError as error:
            print(error)

        print("End of loop")
        client_sock.close()

    # Close the Socket
    server_sock.close()
    print("Socket closed")


if __name__ == "__main__":
    main()
