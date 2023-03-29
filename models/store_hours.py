from sqlalchemy import Column, Integer, String, TIME 
from models.base import Base

metadata = Base.metadata
class StoreHours(Base):

    __tablename__ = "store_hours"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String)
    day = Column(Integer)
    start_time_local = Column(TIME)
    end_time_local = Column(TIME)

