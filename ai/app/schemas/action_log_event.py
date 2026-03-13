from app.schemas.base import CamelModel
from app.schemas.action_type import ActionType


class ActionLogEvent(CamelModel):
    action_log_id: int
    actor_user_id: int
    project_id: int
    topic_id: int
    action_type: ActionType
