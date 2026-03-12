from __future__ import annotations

from enum import Enum


class ActionType(str, Enum):
    IMPRESSION = "IMPRESSION"
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    BOOKMARK = "BOOKMARK"
    VIEW_DETAIL = "VIEW_DETAIL"
    VIEW_SPECIFICATION = "VIEW_SPECIFICATION"

    @property
    def weight(self) -> float:
        return {
            ActionType.IMPRESSION: 0.1,
            ActionType.LIKE: 1.0,
            ActionType.DISLIKE: -1.0,
            ActionType.BOOKMARK: 0.7,
            ActionType.VIEW_DETAIL: 0.3,
            ActionType.VIEW_SPECIFICATION: 0.5,
        }[self]

    @classmethod
    def preference_initializable(cls) -> tuple["ActionType", ...]:
        return (
            cls.LIKE,
            cls.DISLIKE,
            cls.BOOKMARK,
            cls.VIEW_DETAIL,
            cls.VIEW_SPECIFICATION,
        )

    @classmethod
    def preference_initializable_values(cls) -> list[str]:
        return [action_type.value for action_type in cls.preference_initializable()]
