"""Backward-compatible import shim for renamed payung package."""

from payung import preprocess as _preprocess
from payung.preprocess import *  # noqa: F401,F403

globals().update(_preprocess.__dict__)
