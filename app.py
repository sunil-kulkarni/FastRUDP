from fastapi import FastAPI
from udp_client import request_file

app = FastAPI()

SERVER_IP = "192.168.68.108" 


@app.get("/")
def home():
    return {"message": "UDP File Transfer Client"}


@app.get("/download/{filename}")
def download_file(filename: str):

    result = request_file(filename, SERVER_IP)

    if result:
        return {"status": "success", "file": filename}
    else:
        return {"status": "failed"}