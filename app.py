from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
from udp_client import download_file

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/download/{filename}")
async def download(filename: str):
    async def event_stream():
        queue = asyncio.Queue()

        def callback(progress, speed, eta):
            data = {
                "progress": progress,
                "speed": f"{round(speed/1024, 2)} KB/s",
                "eta": f"{round(eta, 2)} sec"
            }
            queue.put_nowait(data)

        # Run download in thread
        import threading
        success = [False]

        def run_download():
            success[0] = download_file(filename, callback)
            queue.put_nowait({"status": "success" if success[0] else "failed"})

        thread = threading.Thread(target=run_download)
        thread.start()

        while True:
            data = await queue.get()
            yield f"data: {json.dumps(data)}\n\n"
            if "status" in data:
                break

    return StreamingResponse(event_stream(), media_type="text/event-stream")
