import socket

SERVER_PORT = 10000

def request_file(filename, server_ip):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    server = (server_ip, SERVER_PORT)

    sock.sendto(filename.encode(), server)

    with open("r_" + filename, "w") as f:

        while True:
            try:
                data, _ = sock.recvfrom(4096)
            except:
                return False

            text = data.decode()

            if text == "FNF":
                return False

            f.write(text)

            sock.sendto("ACK".encode(), server)

            if len(text) < 500:
                break

    sock.close()

    return True