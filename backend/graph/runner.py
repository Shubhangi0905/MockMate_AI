from __future__ import annotations

from functools import lru_cache

from backend.graph.interview_graph import build_graph


@lru_cache(maxsize=1)
def _graph():
    return build_graph()


def run_graph_step(state: dict) -> dict:
    return _graph().invoke(state)

