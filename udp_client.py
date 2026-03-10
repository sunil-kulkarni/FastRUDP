import socket
import hashlib
import json
import os

SERVER_IP = "192.168.68.108"  
SERVER_PORT = 10000

BUFFER_SIZE = 4096
PACKET_SIZE = 500

DOWNLOAD_FOLDER = "downloads"


def request_file(filename):

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    output_file = os.path.join(DOWNLOAD_FOLDER, "r_" + filename)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    server = (SERVER_IP, SERVER_PORT)

    try:

        sock.sendto(filename.encode(), server)

        with open(output_file, "w") as f:

            expected_seq = 0

            while True:

                packet_bytes, _ = sock.recvfrom(BUFFER_SIZE)

                packet = json.loads(packet_bytes.decode())

                seq = packet["seq"]
                data = packet["data"]
                checksum = packet["checksum"]
                length = packet["length"]

                # file not found
                if data == "FNF":
                    print("File not found on server")
                    os.remove(output_file)
                    return False

                # verify checksum
                client_hash = hashlib.sha256(data.encode()).hexdigest()

                if client_hash != checksum:
                    print("Checksum mismatch")
                    continue

                if seq == expected_seq:

                    f.write(data)

                    sock.sendto(str(seq).encode(), server)

                    expected_seq += 1

                    if length < PACKET_SIZE:
                        break

                else:
                    print("Out of order packet")

        return True

    except Exception as e:

        print("Transfer failed:", e)

        if os.path.exists(output_file):
            os.remove(output_file)

        return False

    finally:
        sock.close()