from sqlalchemy import Column, Integer, DateTime, func
from app.db.database import Base

class BaseModelClass(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    create_at = Column(DateTime, server_default=func.now())
    update_at = Column(DateTime, server_default=func.now(), onupdate=func.now())