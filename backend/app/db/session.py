import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Fallback to localhost if env var is missing (useful for local testing outside docker)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://yukti_user:yukti_password_secure@localhost:5432/yukti_db")

engine = create_engine(DATABASE_URL, echo=False) # Set to True later if you want to see SQL queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
