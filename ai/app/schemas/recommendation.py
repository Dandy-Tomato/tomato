from typing import List, Optional
from app.schemas.base import CamelModel

class RecommendationRequest(CamelModel):
    projectId: int
    domainIds: List[int]
    preferenceEmbeddings: Optional[List[float]] = None
    

class TopicItem(CamelModel):
    topic_id: int
    topic_title: str
    topic_description: str
    estimated_development_period: int
    recommended_team_size: int
    difficulty: int
    domain_id: int
    reference_repo_id: int
    recommendation_score: float
    
class RecommendationResponse(CamelModel):
    topics: List[TopicItem]
