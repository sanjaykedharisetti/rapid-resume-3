"""
Semantic similarity using Sentence Transformers.

The model is loaded once at module import time (or lazily on first use).
Model loading failures are handled gracefully – the service returns None
so the scoring layer can apply a documented fallback.
"""
from __future__ import annotations

import logging
import threading
from typing import Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Pre-import scikit-learn modules at top-level to eliminate the ~2.5s cold-import overhead
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
    _SKLEARN_AVAILABLE = True
except Exception:
    _SKLEARN_AVAILABLE = False

_model_lock = threading.Lock()
_model = None          # type: ignore
_model_name: str = ""
_model_error: str = ""
_model_ready: bool = False
_embedding_cache: Dict[str, np.ndarray] = {}


def init_model(model_name: str = "all-MiniLM-L6-v2") -> bool:
    """
    Load the sentence-transformer model.
    Called once during application startup.
    Returns True on success, False on failure.
    """
    global _model, _model_name, _model_error, _model_ready

    with _model_lock:
        if _model_ready:
            return True

        _model_name = model_name
        logger.info("Loading sentence-transformer model '%s' …", model_name)

        try:
            from sentence_transformers import SentenceTransformer
            # Try fast local-only load first to avoid network checks
            try:
                _model = SentenceTransformer(model_name, local_files_only=True)
            except Exception:
                _model = SentenceTransformer(model_name)
            _model_ready = True
            logger.info("Model '%s' loaded successfully.", model_name)
            return True
        except Exception as exc:
            _model_error = str(exc)
            logger.error("Failed to load model '%s': %s", model_name, exc)
            return False


def is_model_ready() -> bool:
    return _model_ready


def get_model_error() -> str:
    return _model_error


def compute_semantic_similarity(text_a: str, text_b: str) -> Optional[float]:
    """
    Compute cosine similarity between two texts using Sentence Transformers.

    Returns a float in [0, 1], or None if the model is not available.
    """
    if not _model_ready or _model is None:
        logger.warning("Semantic model not ready; skipping semantic similarity.")
        return None

    try:
        vec_a = _embedding_cache.get(text_a)
        vec_b = _embedding_cache.get(text_b)

        if vec_a is None and vec_b is None:
            embeddings = _model.encode([text_a, text_b], convert_to_numpy=True, show_progress_bar=False)
            vec_a = np.ravel(np.asarray(embeddings[0]))
            vec_b = np.ravel(np.asarray(embeddings[1]))
            _embedding_cache[text_a] = vec_a
            _embedding_cache[text_b] = vec_b
        else:
            if vec_a is None:
                encoded_a = _model.encode(text_a, convert_to_numpy=True, show_progress_bar=False)
                vec_a = np.ravel(np.asarray(encoded_a))
                _embedding_cache[text_a] = vec_a
            if vec_b is None:
                encoded_b = _model.encode(text_b, convert_to_numpy=True, show_progress_bar=False)
                vec_b = np.ravel(np.asarray(encoded_b))
                _embedding_cache[text_b] = vec_b

        # Cosine similarity
        dot = float(np.dot(vec_a, vec_b))
        norm_a = float(np.linalg.norm(vec_a))
        norm_b = float(np.linalg.norm(vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        similarity = dot / (norm_a * norm_b)
        # Clamp to [0, 1] (similarity can theoretically be slightly negative)
        return float(max(0.0, min(1.0, similarity)))

    except Exception as exc:
        logger.error("Error computing semantic similarity: %s", exc)
        return None



def compute_tfidf_similarity(text_a: str, text_b: str) -> float:
    """
    Fallback: TF-IDF cosine similarity using scikit-learn.
    Always returns a float in [0, 1].
    """
    if not _SKLEARN_AVAILABLE:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
        score = float(sk_cosine(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        return max(0.0, min(1.0, score))
    except Exception as exc:
        logger.error("TF-IDF similarity failed: %s", exc)
        return 0.0

