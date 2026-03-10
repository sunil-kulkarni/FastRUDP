import socket
import hashlib
import json
import os
import base64

SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 10000

PACKET_SIZE = 500
WINDOW_SIZE = 5
TIMEOUT = 2


class Packet:

    def __init__(self, seq, data):
        self.seq = seq
        self.data = data
        self.length = len(data)
        self.checksum = hashlib.sha256(data).hexdigest()

    def encode(self):

        packet_dict = {
            "seq": self.seq,
            "length": self.length,
            "checksum": self.checksum,
            "data": base64.b64encode(self.data).decode()
        }

        return json.dumps(packet_dict).encode()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def handle_client(sock, address, filename):
    filename = filename.strip()
    print(f"Client {address} requested {repr(filename)}")

    try:
        file_path = os.path.join(BASE_DIR, 'files', filename)
        with open(file_path, "rb") as f:
            file_data = f.read()

    except FileNotFoundError:

        error_packet = Packet(0, b"FNF")
        sock.sendto(error_packet.encode(), address)
        print("File not found:", filename)
        return

    packets = []
    seq = 0

    for i in range(0, len(file_data), PACKET_SIZE):
        chunk = file_data[i:i + PACKET_SIZE]
        packets.append(Packet(seq, chunk))
        seq += 1

    base = 0
    next_seq = 0
    total_packets = len(packets)
    while base < total_packets:
        while next_seq < base + WINDOW_SIZE and next_seq < total_packets:
            sock.sendto(packets[next_seq].encode(), address)
            print(f"Sent packet {next_seq}")
            next_seq += 1
        try:
            ack, _ = sock.recvfrom(1024)
            ack = int(ack.decode())
            print(f"ACK received: {ack}")
            if ack >= base:
                base = ack + 1
        except socket.timeout:
            print("Timeout -> Resending window")
            next_seq = base
    print(f"File transfer complete for {filename}")


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_ADDRESS, SERVER_PORT))
print(f"Server running on {SERVER_ADDRESS}:{SERVER_PORT}")

while True:

    data, address = sock.recvfrom(1024)
    filename = data.decode().strip()
    if filename.isdigit():
        continue  # Ignore ACK packets

    print("Requested filename:", repr(filename))
    handle_client(sock, address, filename)