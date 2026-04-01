from typing import List, Optional
from app.schemas.base import CamelModel

class RecommendationRequest(CamelModel):
    project_id: int
    domain_ids: List[int]
    preference_embedding: Optional[List[float]] = None
    

class TopicItem(CamelModel):
    topic_id: int
    title: str
    description: str
    expected_duration_week: int
    recommended_team_size: int
    difficulty: Optional[int] = None
    domain_id: int
    domain_name: str
    source_repo_id: int
    skills: List[int] = []
