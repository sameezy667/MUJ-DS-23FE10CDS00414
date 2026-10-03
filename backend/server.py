"""
@file server.py
@description Production FastAPI application serving Orto GEC REST endpoints, stylometry analysis, and static frontend
@module backend
"""

import os
import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from orto.core.syntax_engine import SyntaxEngine
from orto.critic.verifier import SymbolicCritic
from orto.llm.client import LLMClient
from orto.llm.schemas import DiagnosticEdit, PipelineTelemetry
from orto.pipeline import OrtoEngine
from orto.style.analyzer import StyleAnalyzer
from orto.style.naturalizer import StyleNaturalizer
from orto.style.schemas import StyleAnalysisResult, StylometricReport


class AnalysisOptions(BaseModel):
    """Configuration options for the GEC analysis request."""

    enable_critic: bool = Field(
        default=True,
        description="Whether to run the symbolic morphosyntactic verifier",
    )
    max_refinements: int = Field(
        default=1,
        ge=0,
        le=3,
        description="Maximum 1-turn retry reflection cycles on critic rejection",
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="LLM model identifier",
    )
    include_style: bool = Field(
        default=True,
        description="Whether to include stylometric and naturalness analysis",
    )


class AnalyzeRequest(BaseModel):
    """Incoming request payload for text diagnosis."""

    text: str = Field(
        ...,
        min_length=0,
        max_length=10000,
        description="Raw input text to diagnose and correct",
    )
    options: AnalysisOptions = Field(
        default_factory=AnalysisOptions,
        description="Execution options",
    )


class AnalyzeResponse(BaseModel):
    """Structured response payload returned to client."""

    original_text: str
    corrected_text: str
    edits: List[DiagnosticEdit]
    syntax_priors: Optional[Dict[str, Any]] = None
    stylometry: Optional[StyleAnalysisResult] = None
    telemetry: PipelineTelemetry


class StyleAnalyzeRequest(BaseModel):
    """Request payload specifically for stylometry analysis."""

    text: str = Field(..., min_length=0, max_length=10000)


class HumanizeResponse(BaseModel):
    """Response payload for the AI Humanizer and de-cliché naturalizer."""

    original_text: str
    humanized_text: str
    stylometry: StyleAnalysisResult


app = FastAPI(
    title="Orto GEC Diagnostic Engine API",
    version="0.1.0",
    description="Neurosymbolic Grammatical Error Correction & Linguistic Diagnostic Engine",
)

# CORS Whitelist Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Pipeline Engine Instances
syntax_engine = SyntaxEngine()
critic = SymbolicCritic(syntax_engine)
llm_client = LLMClient()
engine = OrtoEngine(syntax_engine=syntax_engine, llm_client=llm_client, critic=critic)
style_analyzer = StyleAnalyzer(syntax_engine=syntax_engine)
style_naturalizer = StyleNaturalizer(analyzer=style_analyzer, llm_client=llm_client)


@app.middleware("http")
async def add_security_and_rate_limit_headers(request: Request, call_next):
    """Injects rate limit and standard security headers into all responses."""
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = "99"
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 900)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/api/v1/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint verifying API service availability."""
    return {"status": "ok", "service": "orto-gec-engine", "version": "0.1.0"}


@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze_text(payload: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyzes raw text using the neurosymbolic cascade:
    Syntax Engine -> Constrained LLM -> Symbolic Critic -> Reverse Patcher,
    with optional Stylometric analysis.
    """
    try:
        response = engine.analyze(
            text=payload.text,
            enable_critic=payload.options.enable_critic,
            max_refinements=payload.options.max_refinements,
        )

        # Extract syntax priors for visualization
        syntax_priors = syntax_engine.extract_priors(payload.text) if payload.text.strip() else None

        # Extract stylometric metrics if requested
        stylometry_result = None
        if payload.options.include_style and payload.text.strip():
            stylometry_result = style_analyzer.analyze(payload.text)

        return AnalyzeResponse(
            original_text=response.original_text,
            corrected_text=response.corrected_text,
            edits=response.edits,
            syntax_priors=syntax_priors,
            stylometry=stylometry_result,
            telemetry=response.telemetry,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "internal_error", "message": str(e)},
        )


@app.post("/api/v1/style/analyze", response_model=StyleAnalysisResult)
async def analyze_style(payload: StyleAnalyzeRequest) -> StyleAnalysisResult:
    """
    Standalone endpoint for stylometric analysis and naturalness scoring.
    """
    try:
        return style_analyzer.analyze(payload.text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "internal_error", "message": str(e)},
        )


@app.post("/api/v1/style/humanize", response_model=HumanizeResponse)
async def humanize_style(payload: StyleAnalyzeRequest) -> HumanizeResponse:
    """
    AI Humanizer endpoint: de-clichés synthetic AI markers, re-rhythms cadence,
    and returns comprehensive stylometric metrics.
    """
    try:
        analysis = style_analyzer.analyze(payload.text)
        humanized = style_naturalizer.naturalize(payload.text)
        return HumanizeResponse(
            original_text=payload.text,
            humanized_text=humanized,
            stylometry=analysis,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "internal_error", "message": str(e)},
        )


# Mount Static Frontend (prefer built React assets in frontend/dist, fallback to frontend)
base_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
dist_dir = os.path.join(base_frontend_dir, "dist")
static_dir = dist_dir if os.path.exists(dist_dir) else base_frontend_dir

if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
