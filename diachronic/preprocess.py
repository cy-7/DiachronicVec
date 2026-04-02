"""Preprocess raw corpus texts into tokenized sentences."""

import json
import logging
import re
from pathlib import Path

import spacy

from .config import CORPUS_DIR, PERIOD_NAMES, SENTENCES_DIR

LOGGER = logging.getLogger(__name__)

# Patterns to strip Project Gutenberg headers/footers
_GUTENBERG_START = re.compile(
    r"\*\*\*\s*START OF.*?\*\*\*", re.IGNORECASE
)
_GUTENBERG_END = re.compile(
    r"\*\*\*\s*END OF.*?\*\*\*", re.IGNORECASE
)


def _clean_gutenberg(text: str) -> str:
    """Strip Project Gutenberg boilerplate if present."""
    start = _GUTENBERG_START.search(text)
    end = _GUTENBERG_END.search(text)
    if start:
        text = text[start.end():]
    if end:
        text = text[:end.start()]
    return text


def _process_file(nlp: spacy.Language, filepath: Path) -> list[list[str]]:
    """Read one text file and return list of tokenized sentences."""
    raw = filepath.read_text(encoding="utf-8", errors="ignore")
    raw = _clean_gutenberg(raw)

    sentences = []
    for doc in nlp.pipe([raw], n_process=1):
        for sent in doc.sents:
            tokens = [
                t.lemma_.lower()
                for t in sent
                if t.is_alpha and not t.is_stop and len(t.text) > 2
            ]
            if len(tokens) >= 3:
                sentences.append(tokens)
    return sentences


def preprocess_all() -> None:
    """Process all periods and save tokenized sentences as JSON."""
    SENTENCES_DIR.mkdir(parents=True, exist_ok=True)

    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    nlp.max_length = 10_000_000

    for period in PERIOD_NAMES:
        period_dir = CORPUS_DIR / period
        if not period_dir.is_dir():
            LOGGER.warning("Corpus directory not found: %s", period_dir)
            continue

        all_sentences: list[list[str]] = []
        for txt_file in sorted(period_dir.glob("*.txt")):
            LOGGER.info("Processing %s", txt_file.name)
            all_sentences.extend(_process_file(nlp, txt_file))

        out_path = SENTENCES_DIR / f"{period}_sentences.json"
        out_path.write_text(json.dumps(all_sentences, ensure_ascii=False), encoding="utf-8")
        LOGGER.info("%s: %d sentences saved to %s", period, len(all_sentences), out_path)
