from sqlalchemy import Column, Integer, String
from ..database import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    postcode = Column(String, index=True)
    address = Column(String)
    price = Column(Integer)
    property_type = Column(String)
    bedrooms = Column(Integer)
    status = Column(String)