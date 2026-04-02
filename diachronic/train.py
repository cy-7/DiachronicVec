"""Train Word2Vec models for each historical period."""

import json
import logging
import multiprocessing

from gensim.models import Word2Vec

from .config import (
    PERIOD_NAMES, PERIOD_MIN_COUNTS, SENTENCES_DIR, W2V_DIR,
    VECTOR_SIZE, WINDOW, SG, EPOCHS, NEGATIVE, SAMPLE,
)

LOGGER = logging.getLogger(__name__)


def train_all() -> None:
    """Train and save a Word2Vec model for each period."""
    W2V_DIR.mkdir(parents=True, exist_ok=True)
    workers = multiprocessing.cpu_count()

    for period in PERIOD_NAMES:
        src = SENTENCES_DIR / f"{period}_sentences.json"
        if not src.exists():
            raise FileNotFoundError(f"Sentences not found: {src}")

        sentences = json.loads(src.read_text(encoding="utf-8"))
        LOGGER.info("Training %s (%d sentences, min_count=%d)",
                     period, len(sentences), PERIOD_MIN_COUNTS[period])

        model = Word2Vec(
            sentences=sentences,
            vector_size=VECTOR_SIZE,
            window=WINDOW,
            min_count=PERIOD_MIN_COUNTS[period],
            sg=SG,
            epochs=EPOCHS,
            negative=NEGATIVE,
            sample=SAMPLE,
            workers=workers,
        )

        out = W2V_DIR / f"{period}.model"
        model.save(str(out))
        LOGGER.info("Saved %s", out)
