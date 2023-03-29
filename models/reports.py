from sqlalchemy import TIMESTAMP, Column, Integer, String
from sqlalchemy.sql import func

from models.base import Base

metadata = Base.metadata

class Reports(Base):
    __tablename__='reports'

    report_id = Column(String, primary_key=True, index=True)
    report_status = Column(String)
    report = Column(String)
    request_timestamp = Column(TIMESTAMP)
    generation_timestamp = Column(TIMESTAMP)

    def __repr__(self):
        return f"""
        report_id: {self.report_id}, 
        report_status: {self.report_status}, 
        req_ts: {self.request_timestamp}, 
        """