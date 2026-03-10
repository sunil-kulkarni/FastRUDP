import socket
import json
import hashlib
import os
import time
import base64

SERVER_ADDRESS = "server ip address"
SERVER_PORT = 10000
BUFFER_SIZE = 4096
PACKET_SIZE = 500


def download_file(filename, progress_callback):

    os.makedirs("downloads", exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    server = (SERVER_ADDRESS, SERVER_PORT)

    file_path = os.path.join("downloads", filename)

    received_bytes = 0
    expected_seq = 0
    start_time = None

    try:

        sock.sendto(filename.encode(), server)

        with open(file_path, "wb") as f:

            while True:

                packet_bytes, _ = sock.recvfrom(BUFFER_SIZE)

                packet = json.loads(packet_bytes.decode())

                seq = packet["seq"]
                data_str = packet["data"]
                data = base64.b64decode(data_str)
                checksum = packet["checksum"]
                length = packet["length"]

                # File not found on server
                if data == b"FNF":
                    print("File not found on server")
                    return False

                # Verify checksum
                client_hash = hashlib.sha256(data).hexdigest()

                if client_hash != checksum:
                    print("Checksum mismatch, dropping packet")
                    continue

                # Accept packet
                if seq >= expected_seq:

                    if start_time is None:
                        start_time = time.time()

                    f.write(data)

                    sock.sendto(str(seq).encode(), server)

                    expected_seq += 1
                    received_bytes += len(data)

                    elapsed = time.time() - start_time
                    speed = received_bytes / elapsed if elapsed > 0 else 0

                    progress = min(int(received_bytes / PACKET_SIZE), 100)

                    if length < PACKET_SIZE:
                        progress = 100

                    progress_callback(progress, speed, 0)

                    if length < PACKET_SIZE:
                        break

        print("Download complete:", filename)
        return True

    except socket.timeout:
        print("Connection timed out")
        return False

    except Exception as e:
        print("Download failed:", e)

        if os.path.exists(file_path):
            os.remove(file_path)

        return False

    finally:
        sock.close()