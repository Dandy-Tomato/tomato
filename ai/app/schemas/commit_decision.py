from __future__ import annotations

from enum import Enum


class CommitDecision(str, Enum):
    COMMIT = "COMMIT"
    RETRY = "RETRY"
