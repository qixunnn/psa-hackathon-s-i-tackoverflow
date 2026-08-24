"""FastAPI entry point for the PSA Sentinel pipeline skeleton."""

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.orchestrator.schema_validation import validate
from backend.orchestrator.state_machine import (
    EVENTS_DIRECTORY,
    RUNS_DIRECTORY,
    persist_run,
    run_pipeline,
)


ROUTE_GRAPH_PATH = Path(__file__).resolve().parent / "data" / "route_graph.json"


app = FastAPI(title="PSA Sentinel")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    source_url: str
    note: str | None = None
    article_text: str | None = None


class ManualArticleTextRequest(BaseModel):
    article_text: str


class DecisionRequest(BaseModel):
    decision: Literal["accepted", "dismissed"]
    comment: str | None = None


def _read_json(path: Path):
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Run not found")
    with path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@app.post("/runs", status_code=202)
def create_run(request: RunRequest, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    state = {
        "run_id": run_id,
        "status": "queued",
        "submitted_by": "operator",
        "submitted_at": _now(),
        "source_url": request.source_url,
    }
    validate("run", state)
    RUNS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    persist_run(state)
    background_tasks.add_task(
        run_pipeline,
        run_id,
        request.source_url,
        request.note,
        request.article_text,
    )
    return {"run_id": run_id}


@app.post("/runs/{run_id}/article-text", status_code=202)
def resume_run_with_article_text(
    run_id: str,
    request: ManualArticleTextRequest,
    background_tasks: BackgroundTasks,
):
    run_path = RUNS_DIRECTORY / f"{run_id}.json"
    state = _read_json(run_path)
    if state["status"] != "awaiting_manual_text":
        raise HTTPException(status_code=409, detail="Run is not awaiting manual article text")
    article_text = request.article_text.strip()
    if not article_text:
        raise HTTPException(status_code=422, detail="article_text must not be empty")
    state["status"] = "queued"
    persist_run(state)
    background_tasks.add_task(
        run_pipeline,
        run_id,
        state["source_url"],
        None,
        article_text,
    )
    return {"run_id": run_id, "status": "queued"}


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    return _read_json(RUNS_DIRECTORY / f"{run_id}.json")


@app.get("/runs/{run_id}/events")
def get_run_events(run_id: str):
    return _read_json(EVENTS_DIRECTORY / f"{run_id}.json")


@app.get("/routes")
def get_routes():
    return _read_json(ROUTE_GRAPH_PATH)


@app.get("/runs")
def list_runs():
    runs = []
    for path in sorted(RUNS_DIRECTORY.glob("*.json")):
        state = _read_json(path)
        runs.append({
            "run_id": state["run_id"],
            "source_url": state["source_url"],
            "status": state["status"],
            "submitted_at": state["submitted_at"],
            "relevant": state.get("event", {}).get("relevant"),
            "severity": state.get("risk_assessment", {}).get("severity"),
            "probability": state.get("risk_assessment", {}).get("probability"),
            "operator_decision": state.get("advisory", {}).get("operator_decision"),
        })
    return runs


@app.get("/runs/{run_id}/stream")
def stream_run(run_id: str):
    run_path = RUNS_DIRECTORY / f"{run_id}.json"
    if not run_path.is_file():
        raise HTTPException(status_code=404, detail="Run not found")

    def events():
        last_status = None
        while True:
            state = _read_json(run_path)
            status = state["status"]
            if status != last_status:
                last_status = status
                yield f"data: {json.dumps({'status': status})}\n\n"
            if status in {"complete", "halted_not_relevant", "error"}:
                return
            time.sleep(0.1)

    return StreamingResponse(events(), media_type="text/event-stream")


@app.post("/runs/{run_id}/decision")
def decide_run(run_id: str, request: DecisionRequest):
    run_path = RUNS_DIRECTORY / f"{run_id}.json"
    state = _read_json(run_path)
    if "advisory" not in state:
        raise HTTPException(status_code=409, detail="Run has no advisory")
    state["advisory"]["operator_decision"] = request.decision
    state["advisory"]["operator_comment"] = request.comment
    validate("advisory", state["advisory"])
    persist_run(state)
    return state["advisory"]
