"""Strict model-output parsing; no model-derived evidence authority."""
from .plans import PlanError, freeze_hypotheses, freeze_falsification_plan

__all__ = ["PlanError", "freeze_hypotheses", "freeze_falsification_plan"]
