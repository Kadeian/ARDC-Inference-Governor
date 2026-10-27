import asyncio
import hmac
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, ConfigDict, Field

from c4l.adapters import load_factory
from c4l.contracts import Limits
from c4l.engine import run
from c4l.telemetry import COST, LATENCY, REQUESTS, UNKNOWN, setup

log = logging.getLogger("c4l.audit")
auth = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app):
    token = os.getenv("API_TOKEN", "")
    if len(token) < 32:
        raise RuntimeError("API_TOKEN must have at least 32 characters")
    adapter = os.getenv("AGENT_FACTORY", "c4l.adapters:DemoAgent")
    policy = os.getenv("POLICY_FACTORY", "c4l.policy:BaselinePolicy")
    if os.getenv("ENVIRONMENT", "local") != "local":
        if adapter == "c4l.adapters:DemoAgent" or policy == "c4l.policy:BaselinePolicy":
            raise RuntimeError("Live environments require reviewed agent and ARDC factories")
    app.state.token = token
    app.state.agent_factory = load_factory(adapter)
    app.state.policy_factory = load_factory(policy)
    app.state.slots = asyncio.Semaphore(4)
    setup()
    yield


app = FastAPI(
    title="Clarity4Life governance API", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None
)


async def authorized(credentials: HTTPAuthorizationCredentials | None = Depends(auth)):
    if credentials is None or not hmac.compare_digest(credentials.credentials, app.state.token):
        raise HTTPException(401, "Unauthorized")


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1, max_length=8000)


@app.get("/health/live")
async def live():
    return {"status": "ok"}


@app.get("/health/ready")
async def ready():
    return {"status": "ready", "mode": os.getenv("ENVIRONMENT", "local")}


@app.get("/metrics", dependencies=[Depends(authorized)])
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/agent", dependencies=[Depends(authorized)])
async def invoke(body: AgentRequest):
    request_id = str(uuid.uuid4())
    if app.state.slots.locked():
        raise HTTPException(429, "Capacity reached", headers={"Retry-After": "5"})
    started = time.monotonic()
    outcome = "error"
    try:
        async with app.state.slots:
            result = await run(body.prompt, app.state.agent_factory(), app.state.policy_factory(), Limits())
        outcome = result["status"]
        COST.inc(float(result["cost"]))
        return {
            "request_id": request_id,
            "status": outcome,
            "reason_code": result["reason"],
            "policy_version": result["policy_version"],
            "steps": result["steps"],
            "cost_usd": str(result["cost"]),
            "text": result["candidate"] if outcome == "completed" else None,
        }
    except TimeoutError:
        outcome = "timeout"
        UNKNOWN.inc()
        raise HTTPException(504, {"request_id": request_id, "reason_code": "deadline"}) from None
    except Exception:
        UNKNOWN.inc()
        raise HTTPException(503, {"request_id": request_id, "reason_code": "execution_failed"}) from None
    finally:
        LATENCY.observe(time.monotonic() - started)
        REQUESTS.labels(outcome).inc()
        log.warning("request_id=%s outcome=%s", request_id, outcome)


# Validation errors must never echo a rejected body (including sensitive values).
@app.exception_handler(RequestValidationError)
async def sanitized_validation_error(request, exc):
    return JSONResponse(
        status_code=422, content={"detail": "Invalid request. Check fields and remove sensitive information."}
    )


from c4l.workforce.routes import router as workforce_router  # noqa: E402

app.include_router(workforce_router, dependencies=[Depends(authorized)])
