"""Bounded, exact-binary non-shell executor. Host isolation remains external."""
from .adapter import Invocation, Observation, run_invocation

__all__ = ["Invocation", "Observation", "run_invocation"]
