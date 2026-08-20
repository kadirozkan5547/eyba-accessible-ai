"""EYBA yerel web uygulaması ve JSON API'si."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.rag.foundry import is_cached
from app.rag.schemas import Answer
from app.services.rag_service import answer_question
from app.settings import settings

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app = FastAPI(
    title=settings.product_name_tr,
    version=settings.app_version,
    docs_url=None,
    redoc_url=None,
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=settings.max_question_chars)


class HealthResponse(BaseModel):
    status: str
    app_version: str
    knowledge_version: str
    index_ready: bool
    models_cached: bool


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "product_name": settings.product_name_tr,
            "app_version": settings.app_version,
            "max_question_chars": settings.max_question_chars,
            "knowledge_version": settings.knowledge_version,
        },
    )


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    index_ready = all(
        path.exists()
        for path in (settings.embeddings_path, settings.chunk_ids_path, settings.index_meta_path)
    )
    models_cached = await run_in_threadpool(
        lambda: is_cached(settings.embedding_model) and is_cached(settings.chat_model)
    )
    return HealthResponse(
        status="ready" if index_ready and models_cached else "not_ready",
        app_version=settings.app_version,
        knowledge_version=settings.knowledge_version,
        index_ready=index_ready,
        models_cached=models_cached,
    )


@app.post("/api/ask", response_model=Answer)
async def ask(payload: AskRequest) -> Answer:
    try:
        return await run_in_threadpool(answer_question, payload.question)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
