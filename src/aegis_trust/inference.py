"""Backward-compatible import shim for renamed payung package."""

from payung import inference as _inference
from payung.inference import *  # noqa: F401,F403

globals().update(_inference.__dict__)
