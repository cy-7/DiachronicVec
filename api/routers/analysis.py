"""Analysis API routes."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from api.main import get_analyzer

router = APIRouter(tags=["analysis"])


class DriftRequest(BaseModel):
    words: list[str]
    benchmark: str = "modern"
    include_stable: bool = True


class NeighborRequest(BaseModel):
    word: str
    top_n: int = 10


class JaccardRequest(BaseModel):
    word: str
    top_n: int = 25


class ScatterRequest(BaseModel):
    words: list[str]
    method: str = "pca"


@router.post("/analysis/drift")
def drift(req: DriftRequest):
    return get_analyzer().drift_series(req.words, req.benchmark, req.include_stable)


@router.post("/analysis/neighbors")
def neighbors(req: NeighborRequest):
    return get_analyzer().neighbor_evolution(req.word, req.top_n)


@router.post("/analysis/jaccard")
def jaccard(req: JaccardRequest):
    return get_analyzer().jaccard_similarity(req.word, req.top_n)


@router.get("/analysis/top-drifters")
def top_drifters(
    start: str = Query("ancient"),
    end: str = Query("contemporary"),
    n: int = Query(20),
):
    return get_analyzer().top_drifters(start, end, n)


@router.post("/analysis/scatter")
def scatter(req: ScatterRequest):
    return get_analyzer().scatter_2d(req.words, req.method)
