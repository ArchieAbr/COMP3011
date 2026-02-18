from sqlalchemy import Column, Integer, String
from ..database import Base

class CrimeStat(Base):
    __tablename__ = "crime_stats"

    id = Column(Integer, primary_key=True, index=True)
    postcode_sector = Column(String, index=True)
    month = Column(String)
    crime_count = Column(Integer)
    category = Column(String)

class MarketTrend(Base):
    __tablename__ = "market_trends"

    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True)
    quarter = Column(String)
    avg_price = Column(Integer)