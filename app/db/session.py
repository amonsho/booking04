from sqlalchemy.orm import sessionmaker
from app.db.database import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

from sqlalchemy.orm import Session

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()