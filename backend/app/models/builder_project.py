from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.models.user import Base

class BuilderProject(Base):
    __tablename__ = "builder_projects"

    id = Column(Integer, primary_key=True, index=True)
    builder_name = Column(String(100), nullable=False)
    project_name = Column(String(200), nullable=False)
    line = Column(String(50), nullable=False)  # Western, Central, Harbour
    zone = Column(String(100), nullable=False) # e.g., "BKC", "Kharghar (Mumbai 2.0)"
    configurations = Column(String(100), nullable=True)
    price_per_sqft = Column(Float, nullable=True)
    rera_id = Column(String(100), nullable=True)
    status = Column(String(50), default="ongoing")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
