"""Deterministic immutable Capability projections; not independent semantic authority."""
from .render import ProjectionError, build_projections, verify_projection_suite

__all__ = ["ProjectionError", "build_projections", "verify_projection_suite"]
