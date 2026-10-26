"""Strict model-output parsing; no model-derived evidence authority."""
from .plans import PlanError, freeze_hypotheses, freeze_falsification_plan
from .candidate import assemble_typed_candidate

__all__ = ["PlanError", "freeze_hypotheses", "freeze_falsification_plan", "assemble_typed_candidate"]
