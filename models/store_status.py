from sqlalchemy import Column, Integer, String, TIMESTAMP 
from models.base import Base

metadata = Base.metadata
class StoreStatus(Base):

    __tablename__ = "store_status"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String)
    status = Column(String)
    timestamp_utc = Column(TIMESTAMP)
