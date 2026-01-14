"""Codebase Analyst Agent - Source Package."""

from .cli import main
from .agent import create_codebase_agent

__version__ = "1.1.5"

__all__ = ["main", "create_codebase_agent"]
