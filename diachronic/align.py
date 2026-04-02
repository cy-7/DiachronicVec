"""Align word vector spaces using Orthogonal Procrustes."""

import logging

import numpy as np
from gensim.models import Word2Vec
from gensim.models.keyedvectors import KeyedVectors
from scipy.linalg import orthogonal_procrustes

from .config import ALIGNED_DIR, HUB_PERIOD, PERIOD_NAMES, W2V_DIR

LOGGER = logging.getLogger(__name__)


def _align_to_target(source_wv: KeyedVectors, target_wv: KeyedVectors) -> KeyedVectors:
    """Rotate source vectors into target space via Orthogonal Procrustes.

    Following Hamilton et al. (2016): normalize, then align without centering.
    """
    shared = sorted(set(source_wv.key_to_index) & set(target_wv.key_to_index))
    if not shared:
        raise ValueError("No shared vocabulary between models.")
    LOGGER.info("Aligning with %d shared words", len(shared))

    src_mat = np.array([source_wv[w] for w in shared])
    tgt_mat = np.array([target_wv[w] for w in shared])

    # L2-normalize rows before Procrustes (standard practice)
    src_mat = src_mat / (np.linalg.norm(src_mat, axis=1, keepdims=True) + 1e-10)
    tgt_mat = tgt_mat / (np.linalg.norm(tgt_mat, axis=1, keepdims=True) + 1e-10)

    R, _ = orthogonal_procrustes(src_mat, tgt_mat)

    # Normalize all source vectors then rotate
    norms = np.linalg.norm(source_wv.vectors, axis=1, keepdims=True) + 1e-10
    normed = source_wv.vectors / norms
    aligned_vectors = normed @ R

    kv = KeyedVectors(vector_size=source_wv.vector_size)
    kv.add_vectors(source_wv.index_to_key, aligned_vectors)
    kv.fill_norms(force=True)
    return kv


def align_all() -> None:
    """Align all period models to the hub period and save."""
    ALIGNED_DIR.mkdir(parents=True, exist_ok=True)

    models: dict[str, KeyedVectors] = {}
    for name in PERIOD_NAMES:
        path = W2V_DIR / f"{name}.model"
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        models[name] = Word2Vec.load(str(path)).wv

    hub_wv = models[HUB_PERIOD]
    # Normalize hub vectors too for consistent cosine space
    norms = np.linalg.norm(hub_wv.vectors, axis=1, keepdims=True) + 1e-10
    hub_normed = KeyedVectors(vector_size=hub_wv.vector_size)
    hub_normed.add_vectors(hub_wv.index_to_key, hub_wv.vectors / norms)
    hub_normed.fill_norms(force=True)
    hub_normed.save(str(ALIGNED_DIR / f"{HUB_PERIOD}_aligned.kv"))
    LOGGER.info("Saved hub: %s", HUB_PERIOD)

    for name in PERIOD_NAMES:
        if name == HUB_PERIOD:
            continue
        aligned = _align_to_target(models[name], hub_wv)
        aligned.save(str(ALIGNED_DIR / f"{name}_aligned.kv"))
        LOGGER.info("Aligned and saved: %s", name)
