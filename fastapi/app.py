import os
from typing import Optional

import requests
from fastapi import FastAPI, Response, HTTPException, Header
from pydantic import BaseModel

app = FastAPI()

API_KEY = os.getenv("API_KEY")


class AskRequest(BaseModel):
    prompt: str
    context: Optional[str] = None


# Route to check if the FastAPI server is running
@app.get('/ping')
def ping():
    return {"status": "Server is running"}


def check_authorization(auth_key: str):
    if auth_key is None or auth_key != API_KEY:
        print(f"Invalid API key: {auth_key} {API_KEY}")
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post('/ask')
def ask(request: AskRequest, authorization: str = Header(None)):
    try:
        check_authorization(authorization)
    except HTTPException:
        return Response(status_code=401)

    payload = {
        "model": "llama3.1",
        "prompt": request.prompt,
        "stream": False,
        "options": {
            "top_k": 20,
            "top_p": 0.75,
            "temperature": 0.5,
        }
    }

    if request.context:
        payload["context"] = request.context

    try:
        res = requests.post('http://ollama:11434/api/generate', json=payload)
        res.raise_for_status()
        return Response(content=res.text, media_type="application/json")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Llama: {str(e)}")
