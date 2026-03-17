"""Backward-compatible import shim for renamed payung package."""

from payung import reporting as _reporting
from payung.reporting import *  # noqa: F401,F403

globals().update(_reporting.__dict__)
