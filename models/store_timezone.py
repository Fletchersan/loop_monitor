from sqlalchemy import Column, Integer, String 
from models.base import Base

metadata = Base.metadata
class StoreTimezones(Base):

    __tablename__ = "store_timezones"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String)
    timezone_str = Column(String)

    def __repr__(self) -> str:
        return f"""store_id: {self.store_id}, tz_str: {self.timezone_str}"""
