
from typing import Optional
import os
import logging
import dotenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
)
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    logging.warning("GOOGLE_API_KEY not set; requests to Gemini will likely fail.")

app = FastAPI(title="FastAPI Gemini Proxy", version="0.1")


class GenerateRequest(BaseModel):
    prompt: str
    debug: Optional[bool] = False


class GenerateResponse(BaseModel):
    text: str
    raw: Optional[dict] = None


async def call_gemini(payload: dict) -> dict:
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY or "",
    }
    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(GEMINI_URL, json=payload, headers=headers)
        try:
            data = resp.json()
        except Exception:
            raise HTTPException(status_code=502, detail="Invalid JSON from Gemini API")

        if resp.status_code >= 400:
            # Forward Gemini's error body for diagnostics
            raise HTTPException(status_code=resp.status_code, detail=data)

        return data


def extract_text_from_gemini(response_json: dict) -> Optional[str]:
    # Common path: response_json["candidates"][0]["content"]["parts"][0]["text"]
    try:
        candidates = response_json.get("candidates")
        if not candidates:
            return None
        first = candidates[0]
        return (
            first.get("content", {}).get("parts", [])[0].get("text")
            if first.get("content")
            else None
        )
    except Exception:
        return None


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt must be a non-empty string")

    payload = {
        "contents": [
            {"parts": [{"text": req.prompt}], "role": "user"}
        ]
    }

    gemini_resp = await call_gemini(payload)
    neat_text = extract_text_from_gemini(gemini_resp) or "(no textual candidate found)"

    if req.debug:
        return {"text": neat_text, "raw": gemini_resp}
    return {"text": neat_text}


# Optional health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
