from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.connection import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    workbook_id = Column(Integer, ForeignKey("workbooks.id"), nullable=False)

    inventory_id = Column(Integer, ForeignKey("inventories.id"), nullable=False)
    celery_task_id = Column(String(255), nullable=True)
    progress = Column(Integer, default=0)

    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(String(20), default="queued")   

    result = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)

    finished_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())