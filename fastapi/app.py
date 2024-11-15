import asyncio
import os
import time

import requests
from pydantic import BaseModel

from fastapi import FastAPI, Response, HTTPException, Header

app = FastAPI()
queue_semaphore = asyncio.Semaphore(2)
pending_requests = 0
API_KEY = os.getenv("API_KEY")


class AskRequest(BaseModel):
    prompt: str


# Route to check if the FastAPI server is running
@app.get('/ping')
def ping():
    return {"status": "Server is running"}


def check_authorization(auth_key: str):
    if auth_key is None or auth_key != API_KEY:
        print(f"Invalid API key: {auth_key} {API_KEY}")
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post('/ask')
async def ask(request: AskRequest, authorization: str = Header(None)):
    global pending_requests
    try:
        check_authorization(authorization)
    except HTTPException:
        return Response(status_code=401)

    payload = {
        "model": "llama3.2:3b",
        "prompt": request.prompt,
        "stream": False,
        "format": "json",
        "options": {
            "top_k": 20,
            "top_p": 0.75,
            "temperature": 0.5,
        }
    }

    pending_requests += 1
    start_time = time.time_ns()
    print(f"\nNew request, pending requests: {pending_requests}\nLength of prompt: {len(request.prompt)}\n")
    async with queue_semaphore:
        try:
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, lambda: requests.post('http://ollama:11434/api/generate', json=payload))
            res.raise_for_status()
            return Response(content=res.text, media_type="application/json")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error communicating with Llama: {str(e)}")
        finally:
            pending_requests -= 1
            print(f"\nRequest completed.\nTime taken: {(time.time_ns() - start_time) / 1e9}\nPending requests: {pending_requests}\n")
