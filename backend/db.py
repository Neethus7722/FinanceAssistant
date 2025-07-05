# Database models and SQLAlchemy setup for financial data
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, MetaData
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/finance_db")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class FinancialRecord(Base):
    __tablename__ = 'financials'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Add more columns dynamically or via Alembic migration for production
    # Example static columns:
    revenue = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    margin = Column(Float, nullable=True)
    project = Column(String(255), nullable=True)
    # ... add more as needed
