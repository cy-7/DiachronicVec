"""Shared utility functions."""

import numpy as np


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine distance between two vectors."""
    sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(1.0 - sim)


def batch_cosine_distances(matrix: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Compute cosine distances between each row of matrix and target vector."""
    norms = np.linalg.norm(matrix, axis=1)
    target_norm = np.linalg.norm(target)
    sims = matrix @ target / (norms * target_norm + 1e-10)
    return 1.0 - sims
