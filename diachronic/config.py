"""Centralized project configuration."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

CORPUS_DIR = ROOT_DIR / "corpus"
SENTENCES_DIR = ROOT_DIR / "data" / "sentences"
W2V_DIR = ROOT_DIR / "models" / "word2vec"
ALIGNED_DIR = ROOT_DIR / "models" / "aligned"
RESULTS_DIR = ROOT_DIR / "results"

PERIODS = [
    {"name": "ancient", "year": -400, "min_count": 7},
    {"name": "medieval", "year": 1200, "min_count": 5},
    {"name": "modern", "year": 1800, "min_count": 10},
    {"name": "contemporary", "year": 2000, "min_count": 2},
]

PERIOD_NAMES = [p["name"] for p in PERIODS]
PERIOD_YEARS = {p["name"]: p["year"] for p in PERIODS}
PERIOD_MIN_COUNTS = {p["name"]: p["min_count"] for p in PERIODS}

HUB_PERIOD = "modern"

VECTOR_SIZE = 300
WINDOW = 5
SG = 1          # Skip-gram (standard for diachronic semantics, Hamilton et al. 2016)
EPOCHS = 15
NEGATIVE = 10
SAMPLE = 1e-4   # subsampling threshold for frequent words

TARGET_WORDS = ["reason", "god", "nature", "law"]
STABLE_WORDS = ["body", "hand", "stone", "animal"]

PERIOD_COLORS = {
    "ancient": "#D97706",
    "medieval": "#4F46E5",
    "modern": "#059669",
    "contemporary": "#DB2777",
}
