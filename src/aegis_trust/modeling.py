"""Backward-compatible import shim for renamed payung package."""

from payung import modeling as _modeling
from payung.modeling import *  # noqa: F401,F403

globals().update(_modeling.__dict__)
