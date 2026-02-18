from sqlalchemy import Column, Float, Integer, String, Index

from ..database import Base


class AreaMetric(Base):
    __tablename__ = "area_metrics"
    __table_args__ = (
        Index("ix_area_metrics_postcode_period", "postcode_sector", "period", unique=True),
    )

    id = Column(Integer, primary_key=True, index=True)
    postcode_sector = Column(String, index=True)
    period = Column(String)
    safety_score = Column(Integer)
    affordability_index = Column(Integer)
    yield_estimate = Column(Float)
