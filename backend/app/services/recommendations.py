from sqlalchemy import select
from app.models.builder_project import BuilderProject
from sqlalchemy.ext.asyncio import AsyncSession

async def get_recommendations(db: AsyncSession, max_loan: float):
    """Finds projects where a 700 sqft flat is within the user's loan eligibility."""
    result = await db.execute(select(BuilderProject))
    projects = result.scalars().all()
    
    recommended = []
    for p in projects:
        if p.price_per_sqft:
            # Assume a modest 700 sqft carpet area for entry-level buying
            estimated_cost = p.price_per_sqft * 700
            if estimated_cost <= max_loan:
                recommended.append({
                    "project": p.project_name,
                    "zone": p.zone,
                    "line": p.line,
                    "price_per_sqft": p.price_per_sqft,
                    "estimated_cost": estimated_cost
                })
                
    # Sort by closest to max budget (best use of funds)
    recommended.sort(key=lambda x: x["estimated_cost"], reverse=True)
    return recommended[:3]
