"""Backward-compatible import shim for renamed payung package."""

from payung import llm as _llm
from payung.llm import *  # noqa: F401,F403

globals().update(_llm.__dict__)
