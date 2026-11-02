from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.connection import Base


class Workbook(Base):
    __tablename__ = "workbooks"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    content = Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


class WorkbookVersion(Base):
    """Immutable snapshot of a workbook's content; every real change adds a row."""
    __tablename__ = "workbook_versions"

    id = Column(Integer, primary_key=True, index=True)
    workbook_id = Column(Integer, ForeignKey("workbooks.id"), nullable=False, index=True)
    version_no = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    change_notes = Column(String(255), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
