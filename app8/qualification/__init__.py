"""Stored-Evidence scoped qualification; never runs software or signs evidence."""
from .service import Qualification, qualify_stored_capability

__all__ = ["Qualification", "qualify_stored_capability"]
