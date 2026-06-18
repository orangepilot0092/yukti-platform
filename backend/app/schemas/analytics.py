from pydantic import BaseModel
from typing import Optional

class IntentCount(BaseModel):
    intent: str
    count: int

class StageCount(BaseModel):
    stage: str
    count: int

class ScoreDistribution(BaseModel):
    bucket: str  # e.g., "0-20", "21-40", "41-60", "61-80", "81-100"
    count: int

class PipelineAnalytics(BaseModel):
    total_leads: int
    qualified_leads: int
    avg_score: Optional[float]
    intent_breakdown: list[IntentCount]
    stage_breakdown: list[StageCount]
    score_distribution: list[ScoreDistribution]
