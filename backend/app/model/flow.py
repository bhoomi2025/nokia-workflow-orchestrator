from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.connection import Base


class Flow(Base):
    __tablename__ = "flows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FlowStep(Base):
    __tablename__ = "flow_steps"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False)
    position = Column(Integer, nullable=False)
    workbook_id = Column(Integer, ForeignKey("workbooks.id"), nullable=False)
    var_overrides = Column(Text, nullable=True)            
    on_error = Column(String(20), default="stop")             