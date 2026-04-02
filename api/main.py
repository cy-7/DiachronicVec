"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from diachronic.analyze import Analyzer


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.analyzer = Analyzer()
    yield


app = FastAPI(title="DiachronicVec API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_analyzer() -> Analyzer:
    return app.state.analyzer


from api.routers import analysis, corpus  # noqa: E402

app.include_router(analysis.router, prefix="/api")
app.include_router(corpus.router, prefix="/api")
