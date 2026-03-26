from __future__ import annotations

from enum import Enum


class ActionType(str, Enum):
    IMPRESSION = "IMPRESSION"

    LIKE = "LIKE"
    LIKE_CANCEL = "LIKE_CANCEL"

    DISLIKE = "DISLIKE"
    DISLIKE_CANCEL = "DISLIKE_CANCEL"

    BOOKMARK = "BOOKMARK"
    BOOKMARK_CANCEL = "BOOKMARK_CANCEL"

    VIEW_DETAIL = "VIEW_DETAIL"
    VIEW_SPECIFICATION = "VIEW_SPECIFICATION"

    @property
    def weight(self) -> float:
        return {
            ActionType.IMPRESSION: 0.0,

            ActionType.LIKE: 0.3,
            ActionType.LIKE_CANCEL: -0.3,

            ActionType.DISLIKE: -0.2,
            ActionType.DISLIKE_CANCEL: 0.2,

            ActionType.BOOKMARK: 0.2,
            ActionType.BOOKMARK_CANCEL: -0.2,

            ActionType.VIEW_DETAIL: 0.06,
            ActionType.VIEW_SPECIFICATION: 0.1,
        }[self]

    @classmethod
    def preference_initializable(cls) -> tuple["ActionType", ...]:
        return (
            cls.LIKE,
            cls.LIKE_CANCEL,
            cls.DISLIKE,
            cls.DISLIKE_CANCEL,
            cls.BOOKMARK,
            cls.BOOKMARK_CANCEL,
            cls.VIEW_DETAIL,
            cls.VIEW_SPECIFICATION,
        )

    @classmethod
    def preference_initializable_values(cls) -> list[str]:
        return [action_type.value for action_type in cls.preference_initializable()]
