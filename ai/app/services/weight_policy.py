from app.schemas.action_type import ActionType


ACTION_WEIGHTS: dict[ActionType, float] = {
    ActionType.IMPRESSION: 0.1,
    ActionType.LIKE: 1.0,
    ActionType.DISLIKE: -1.0,
    ActionType.BOOKMARK: 0.7,
    ActionType.VIEW_DETAIL: 0.3,
    ActionType.VIEW_SPECIFICATION: 0.5,
}

def get_action_weight(action_type: ActionType) -> float:
    return ACTION_WEIGHTS[action_type]
