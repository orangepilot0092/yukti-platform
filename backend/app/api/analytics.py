from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, case
from app.models.lead import Lead
from app.schemas.analytics import PipelineAnalytics, IntentCount, StageCount, ScoreDistribution

# Async DB setup embedded here
DATABASE_URL = "postgresql+asyncpg://yukti_user:yukti_password_secure@db:5432/yukti_db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/pipeline", response_model=PipelineAnalytics)
async def get_pipeline_analytics(db: AsyncSession = Depends(get_async_db)):
    """Builder Dashboard: Aggregated metrics for pipeline health."""
    
    # 1. Total & Qualified Leads
    total_q = await db.execute(select(func.count(Lead.id)))
    total_leads = total_q.scalar() or 0
    
    qual_q = await db.execute(select(func.count(Lead.id)).where(Lead.score >= 70))
    qualified_leads = qual_q.scalar() or 0
    
    # 2. Average Score
    avg_q = await db.execute(select(func.avg(Lead.score)))
    avg_score = avg_q.scalar()
    
    # 3. Intent Breakdown
    intent_q = await db.execute(
        select(Lead.intent, func.count(Lead.id))
        .group_by(Lead.intent)
        .order_by(func.count(Lead.id).desc())
    )
    intent_breakdown = [IntentCount(intent=str(row[0] or "unknown"), count=row[1]) for row in intent_q.all()]
    
    # 4. Stage Breakdown
    stage_q = await db.execute(
        select(Lead.stage, func.count(Lead.id))
        .group_by(Lead.stage)
        .order_by(func.count(Lead.id).desc())
    )
    stage_breakdown = [StageCount(stage=str(row[0] or "unknown"), count=row[1]) for row in stage_q.all()]
    
    # 5. Score Distribution (Buckets)
    score_dist_q = await db.execute(
        select(
            case(
                (Lead.score < 20, "0-20"),
                (Lead.score < 40, "21-40"),
                (Lead.score < 60, "41-60"),
                (Lead.score < 80, "61-80"),
                else_="81-100"
            ).label("bucket"),
            func.count(Lead.id)
        )
        .group_by("bucket")
        .order_by("bucket")
    )
    score_distribution = [ScoreDistribution(bucket=row[0], count=row[1]) for row in score_dist_q.all()]
    
    return PipelineAnalytics(
        total_leads=total_leads,
        qualified_leads=qualified_leads,
        avg_score=round(avg_score, 2) if avg_score else None,
        intent_breakdown=intent_breakdown,
        stage_breakdown=stage_breakdown,
        score_distribution=score_distribution
    )
