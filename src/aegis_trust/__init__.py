"""Backward-compatible import shim for renamed payung package."""

from payung import *  # noqa: F401,F403
from payung import __dict__ as _payung_dict

globals().update(_payung_dict)
