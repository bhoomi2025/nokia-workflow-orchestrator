from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.connection import Base


class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    hosts = Column(Text, nullable=True)      

    groups = Column("groups_json", Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)

    inventory_id = Column(Integer, ForeignKey("inventories.id"), nullable=False)

    host_name = Column(String(100), nullable=False)

    username = Column(String(100), nullable=False)

    encrypted_secret = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())