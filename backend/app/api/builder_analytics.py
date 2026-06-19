from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.models.deal import Deal
from app.models.lead import Lead
from app.models.builder_project import BuilderProject

DATABASE_URL = "postgresql+asyncpg://yukti_user:yukti_password_secure@db:5432/yukti_db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter(prefix="/builder", tags=["builder_enterprise"])

class CPPerformance(BaseModel):
    cp_name: str
    total_deals: int
    total_volume: float
    avg_lead_score: Optional[float]
    avg_loan_eligibility: Optional[float]
    primary_transit_line: Optional[str]

@router.get("/analytics/cp-leaderboard", response_model=list[CPPerformance])
async def get_cp_leaderboard(db: AsyncSession = Depends(get_async_db)):
    """
    Enterprise Builder Dashboard: Ranks CPs by financial verification and deal volume.
    Proves which CPs bring loan-ready buyers vs. junk leads.
    """
    stmt = (
        select(
            Deal.cp_name,
            func.count(Deal.id).label("total_deals"),
            func.sum(Deal.deal_value).label("total_volume"),
            func.avg(Lead.score).label("avg_lead_score"),
            func.avg(Lead.max_loan_eligibility).label("avg_loan_eligibility"),
            # Get the most common transit line for this CP's deals (simplified via max for grouping)
            func.max(BuilderProject.line).label("primary_transit_line")
        )
        .join(Lead, Deal.lead_id == Lead.id)
        .join(BuilderProject, Deal.project_id == BuilderProject.id)
        .where(Deal.cp_name.isnot(None))
        .group_by(Deal.cp_name)
        .order_by(func.sum(Deal.deal_value).desc())
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        CPPerformance(
            cp_name=row.cp_name,
            total_deals=row.total_deals,
            total_volume=float(row.total_volume or 0),
            avg_lead_score=round(float(row.avg_lead_score), 2) if row.avg_lead_score else None,
            avg_loan_eligibility=round(float(row.avg_loan_eligibility), 2) if row.avg_loan_eligibility else None,
            primary_transit_line=row.primary_transit_line
        )
        for row in rows
    ]

@router.get("/analytics/transit-heatmap")
async def get_transit_heatmap(db: AsyncSession = Depends(get_async_db)):
    """
    Builder Intelligence: Aggregates total user demand vs converted deals per transit line.
    Uses SQL CASE statements to map extracted locations to Western/Central/Harbour lines.
    """
    from sqlalchemy import case
    
    # Map AI-extracted locations to Transit Lines
    transit_line_expr = case(
        (Lead.preferred_location.in_(["Bandra", "Andheri", "Worli", "Prabhadevi", "Kandivali", "Goregaon", "Malad"]), "Western"),
        (Lead.preferred_location.in_(["Powai", "Vikhroli", "Mulund", "Thane", "Dadar", "Parel", "Bkc"]), "Central"),
        (Lead.preferred_location.in_(["Kharghar", "Ghansoli", "Panvel", "Ulwe", "Vashi", "Nerul", "Navi Mumbai"]), "Harbour"),
        else_="Other"
    ).label("transit_line")

    stmt = (
        select(
            transit_line_expr,
            func.count(Lead.id).label("total_demand_leads"),
            func.count(Deal.id).label("converted_deals"),
            func.coalesce(func.sum(Deal.deal_value), 0).label("total_converted_volume"),
            func.coalesce(func.avg(Lead.max_loan_eligibility), 0).label("avg_buyer_eligibility")
        )
        .outerjoin(Deal, Lead.id == Deal.lead_id)
        .group_by(transit_line_expr)
        .order_by(func.count(Lead.id).desc())
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        {
            "transit_line": row.transit_line,
            "total_demand_leads": row.total_demand_leads,
            "converted_deals": row.converted_deals,
            "total_converted_volume": float(row.total_converted_volume),
            "avg_buyer_eligibility": round(float(row.avg_buyer_eligibility), 2)
        }
        for row in rows
    ]
