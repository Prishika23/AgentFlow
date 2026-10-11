import os

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from google.genai.errors import APIError
from pydantic import BaseModel

from ai.orchestrator import Orchestrator


app = FastAPI(title="AgentFlow Local AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

AGENTFLOW_TOKEN = os.getenv("AGENTFLOW_TOKEN")


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat(
    req: ChatRequest,
    x_agentflow_token: str | None = Header(default=None),
):
    if not AGENTFLOW_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="AGENTFLOW_TOKEN is not configured on the backend.",
        )

    if x_agentflow_token != AGENTFLOW_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized.",
        )

    try:
        return orchestrator.handle(req.session_id, req.message)

    except APIError as exc:
        status_code = (
            exc.code
            if isinstance(exc.code, int) and 400 <= exc.code <= 599
            else 502
        )

        if status_code == 503:
            detail = "Gemini is temporarily unavailable. Please retry in a moment."
        elif status_code == 429:
            detail = "Gemini rate limit reached. Please wait a moment and retry."
        elif status_code in (401, 403):
            detail = "Gemini rejected the API key. Check GEMINI_API_KEY in backend/.env."
        else:
            detail = f"Gemini API request failed (HTTP {status_code})."

        raise HTTPException(
            status_code=status_code,
            detail=detail,
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc