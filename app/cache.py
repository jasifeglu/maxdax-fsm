"""Caching utilities for hot paths."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import TypeVar

from cachetools import TTLCache

T = TypeVar("T")


class AppCache:
    """Small wrapper around TTLCache with observability counters."""

    def __init__(self, maxsize: int, ttl: int) -> None:
        self._cache: TTLCache[str, object] = TTLCache(maxsize=maxsize, ttl=ttl)
        self.hits = 0
        self.misses = 0

    def get_or_compute(self, key: str, provider: Callable[[], T]) -> T:
        """Return a cached item or compute and cache it."""

        if key in self._cache:
            self.hits += 1
            return self._cache[key]  # type: ignore[return-value]

        self.misses += 1
        value = provider()
        self._cache[key] = value
        return value

    def stats(self) -> dict[str, float]:
        """Expose cache hit ratio and entry count for monitoring."""

        total = self.hits + self.misses
        return {
            "hits": float(self.hits),
            "misses": float(self.misses),
            "hit_ratio": float(self.hits / total) if total else 0.0,
            "entries": float(len(self._cache)),
        }


def benchmark(provider: Callable[[], T]) -> tuple[T, float]:
    """Simple helper to track execution time in milliseconds."""

    start = perf_counter()
    value = provider()
    elapsed_ms = (perf_counter() - start) * 1000
    return value, elapsed_ms
