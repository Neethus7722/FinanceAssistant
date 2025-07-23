# Database models and SQLAlchemy setup for financial data with session management
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, MetaData, DateTime, Date, Text
from datetime import datetime
from typing import AsyncGenerator

# Import centralized configuration
from config import get_config

# Get configuration instance
config = get_config()

# Create database engine with centralized configuration
engine = create_async_engine(
    config.database.url, 
    echo=config.database.echo,
    pool_size=config.database.pool_size,
    max_overflow=config.database.max_overflow
)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Dependency for FastAPI to get database session
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection"""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

class FinancialRecord(Base):
    __tablename__ = 'financials'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Time series data for forecasting
    date = Column(Date, nullable=False)
    revenue = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    margin = Column(Float, nullable=True)
    project = Column(String(255), nullable=True)
    region = Column(String(100), nullable=True)
    product_category = Column(String(100), nullable=True)
    sales_rep = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RevenueTimeSeries(Base):
    """Time series data specifically for forecasting models."""
    __tablename__ = 'revenue_time_series'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ds = Column(Date, nullable=False)  # Prophet convention: 'ds' for date
    y = Column(Float, nullable=False)  # Prophet convention: 'y' for target variable
    # External regressors for XGBoost
    pipeline_value = Column(Float, nullable=True)
    num_opportunities = Column(Integer, nullable=True)
    avg_deal_size = Column(Float, nullable=True)
    market_index = Column(Float, nullable=True)
    seasonality_factor = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ForecastResults(Base):
    """Store forecast results for comparison and tracking."""
    __tablename__ = 'forecast_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    forecast_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)
    model_type = Column(String(50), nullable=False)  # 'prophet', 'xgboost', 'ensemble'
    predicted_value = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)  # Filled when actual data becomes available
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
