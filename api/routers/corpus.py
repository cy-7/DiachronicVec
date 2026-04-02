"""Corpus info API routes."""

from fastapi import APIRouter, Query

from api.main import get_analyzer
from diachronic.config import PERIODS, PERIOD_COLORS

router = APIRouter(tags=["corpus"])


@router.get("/periods")
def periods():
    return [
        {**p, "color": PERIOD_COLORS[p["name"]]}
        for p in PERIODS
    ]


@router.get("/vocab")
def vocab(period: str = Query(...), limit: int = Query(500)):
    return get_analyzer().vocab_list(period, limit)


@router.get("/corpus/stats")
def stats():
    a = get_analyzer()
    return {
        "periods": len(a.models),
        "shared_vocab": a.shared_vocab_size(),
        "vocab_sizes": {p: len(a.models[p].key_to_index) for p in a.models},
    }
