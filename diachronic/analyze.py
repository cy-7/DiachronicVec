"""Semantic analysis engine — returns data, does not plot."""

import logging
from typing import Any

import numpy as np
from gensim.models.keyedvectors import KeyedVectors
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from .config import ALIGNED_DIR, PERIOD_NAMES, PERIOD_YEARS, STABLE_WORDS
from .utils import cosine_distance

LOGGER = logging.getLogger(__name__)


class Analyzer:
    """Loads aligned models and provides analysis methods returning plain data."""

    def __init__(self) -> None:
        self.models: dict[str, KeyedVectors] = {}
        for name in PERIOD_NAMES:
            path = ALIGNED_DIR / f"{name}_aligned.kv"
            if not path.exists():
                raise FileNotFoundError(f"Aligned model not found: {path}")
            self.models[name] = KeyedVectors.load(str(path), mmap="r")
        # Pre-compute shared vocabulary and per-period shared matrices
        sets = [set(m.key_to_index) for m in self.models.values()]
        self.shared_vocab: set[str] = sets[0].intersection(*sets[1:])
        self._shared_words = sorted(self.shared_vocab)
        self._shared_mats: dict[str, np.ndarray] = {}
        for p in PERIOD_NAMES:
            mat = np.array([self.models[p][w] for w in self._shared_words])
            norms = np.linalg.norm(mat, axis=1, keepdims=True) + 1e-10
            self._shared_mats[p] = mat / norms
        LOGGER.info("Shared vocabulary: %d words", len(self.shared_vocab))

    def _check(self, word: str) -> None:
        missing = [p for p in PERIOD_NAMES if word not in self.models[p]]
        if missing:
            raise KeyError(f"'{word}' not in periods: {missing}")

    def _neighbors_in_shared(self, period: str, word: str, top_n: int) -> list[tuple[str, float]]:
        """Get top-N neighbors restricted to shared vocabulary via matrix cosine."""
        vec = self.models[period][word]
        vec = vec / (np.linalg.norm(vec) + 1e-10)
        sims = self._shared_mats[period] @ vec
        idx = np.argsort(sims)[::-1]
        result = []
        for i in idx:
            w = self._shared_words[i]
            if w != word:
                result.append((w, float(sims[i])))
                if len(result) >= top_n:
                    break
        return result

    def _compute_baseline(self, benchmark: str = "modern") -> list[float]:
        """Compute mean cosine distance of the most stable 25% of shared vocab."""
        if hasattr(self, '_baseline_cache') and self._baseline_cache[0] == benchmark:
            return self._baseline_cache[1]
        shared = sorted(self.shared_vocab)
        # Compute total drift per word across all non-benchmark periods
        drifts = []
        for w in shared:
            bv = self.models[benchmark][w]
            d = sum(float(cosine_distance(self.models[p][w], bv))
                    for p in PERIOD_NAMES if p != benchmark)
            drifts.append(d)
        # Take bottom 25% as "stable" words
        order = np.argsort(drifts)
        n_stable = max(50, len(shared) // 4)
        stable_words = [shared[i] for i in order[:n_stable]]
        # Compute mean drift per period for these stable words
        baseline = []
        for p in PERIOD_NAMES:
            vals = [float(cosine_distance(self.models[p][w], self.models[benchmark][w]))
                    for w in stable_words]
            baseline.append(round(max(0.0, float(np.mean(vals))), 4))
        self._baseline_cache = (benchmark, baseline)
        return baseline

    # --- drift ---
    def drift_series(self, words: list[str], benchmark: str = "modern",
                     include_stable: bool = True) -> dict[str, Any]:
        """Return cosine-distance drift series with computed stable baseline."""
        years = [PERIOD_YEARS[p] for p in PERIOD_NAMES]
        series = {}
        for w in words:
            self._check(w)
            bv = self.models[benchmark][w]
            series[w] = [round(max(0.0, float(cosine_distance(self.models[p][w], bv))), 4)
                         for p in PERIOD_NAMES]
        baseline = self._compute_baseline(benchmark) if include_stable else None
        return {"years": years, "periods": PERIOD_NAMES,
                "series": series, "baseline": baseline}

    # --- neighbors ---
    def neighbor_evolution(self, word: str, top_n: int = 10) -> dict[str, list[dict]]:
        """Return top-N neighbors per period (restricted to shared vocab)."""
        self._check(word)
        result = {}
        for p in PERIOD_NAMES:
            result[p] = [
                {"word": w, "score": round(float(s), 4)}
                for w, s in self._neighbors_in_shared(p, word, top_n)
            ]
        return result

    # --- jaccard ---
    def jaccard_similarity(self, word: str, top_n: int = 25) -> dict[str, Any]:
        """Return Jaccard similarity at multiple k values (shared-vocab neighbors)."""
        self._check(word)
        k_values = [10, 25, 50]
        if top_n not in k_values:
            k_values = sorted(set(k_values + [top_n]))
        pairs = list(zip(PERIOD_NAMES[:-1], PERIOD_NAMES[1:]))
        labels = [f"{a}-{b}" for a, b in pairs]
        results_by_k = {}
        for k in k_values:
            sets = {p: {w for w, _ in self._neighbors_in_shared(p, word, k)}
                    for p in PERIOD_NAMES}
            scores = []
            for a, b in pairs:
                inter = len(sets[a] & sets[b])
                union = len(sets[a] | sets[b]) or 1
                scores.append(round(inter / union, 4))
            results_by_k[k] = scores
        return {"labels": labels, "results_by_k": results_by_k, "scores": results_by_k[top_n]}

    # --- top drifters ---
    def top_drifters(self, start: str = "ancient", end: str = "contemporary",
                     top_n: int = 20) -> list[dict]:
        """Find words with largest semantic drift (vectorized, shared vocab only)."""
        shared = sorted(self.shared_vocab)
        sv = np.array([self.models[start][w] for w in shared])
        ev = np.array([self.models[end][w] for w in shared])
        dots = np.einsum("ij,ij->i", sv, ev)
        norms = np.linalg.norm(sv, axis=1) * np.linalg.norm(ev, axis=1)
        dists = 1.0 - dots / (norms + 1e-10)
        top_idx = np.argsort(dists)[::-1][:top_n]
        return [{"word": shared[i], "distance": round(float(dists[i]), 4)} for i in top_idx]

    # --- 2D scatter ---
    def scatter_2d(self, words: list[str], method: str = "pca") -> dict[str, Any]:
        """Project word vectors across periods into 2D."""
        all_vecs, all_labels, all_periods = [], [], []
        for w in words:
            self._check(w)
            for p in PERIOD_NAMES:
                all_vecs.append(self.models[p][w])
                all_labels.append(w)
                all_periods.append(p)

        mat = np.array(all_vecs)
        if method == "tsne" and len(mat) > 5:
            coords = TSNE(n_components=2, perplexity=min(5, len(mat) - 1),
                          random_state=42).fit_transform(mat)
        else:
            coords = PCA(n_components=2).fit_transform(mat)

        return {
            "points": [
                {"word": all_labels[i], "period": all_periods[i],
                 "x": round(float(coords[i, 0]), 4),
                 "y": round(float(coords[i, 1]), 4)}
                for i in range(len(all_labels))
            ]
        }

    # --- vocab info ---
    def vocab_list(self, period: str, limit: int = 500) -> list[str]:
        return list(self.models[period].key_to_index.keys())[:limit]

    def shared_vocab_size(self) -> int:
        return len(self.shared_vocab)
