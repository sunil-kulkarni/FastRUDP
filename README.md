# FastRUDP

A reliable file transfer protocol built on top of UDP using Python.
Since UDP does not provide reliability, this project implements its own mechanisms for:

* Packet sequencing
* Sliding window flow control
* Acknowledgement handling
* Retransmission on timeout
* Data integrity using SHA256 checksum

### **This project requires the use of two machines**
#### **Machine-1: client-side**
Client side structure:
```bash
├── app.py          #fastapi for serving web control and interface layer
├── downloads/
│   ├── sample.txt
│   └── samp.png
├── requirements.txt
├── static/
│   └── style.css
├── templates/
│   └── index.html          #html for web interaction
└── udp_client.py           #client side udp
```
#### **Machine-2: server-side**
Server side structure:
```bash
server/
├── files/
└── server.py
```
---

## How to run the project
### Client-side:
Create virtual environment and activate
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the requirements
```bash
pip install -r requirements.txt
```

Run the client-side application
```bash
uvicorn app:main --reload
```

### Server-side:
under `files/` include sample files
```bash
server/
├── files/
|    ├── sample.txt
|    └── sample.png
└── server.py
```
Run the server
```bash
python3 server.py
```
After starting both the sides, the user can type in the same of the file and click download.  
The download process will start and also show the progress with network speed.

Enter file name
![alt text](image-1.png)

After downloading
![alt text](image.png)
---

## Architecture:
```bash
Browser / API Client
        │
        │ HTTP GET request
        ▼
      FastAPI
        │
        │ Python function call
        ▼
     UDP Client
        │
        │ UDP packets
        ▼
     UDP Server
```
