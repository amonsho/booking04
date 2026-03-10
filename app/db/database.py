from sqlalchemy import create_engine
from sqlalchemy.orm import Declarative_base

DATABASE_URL = "sqlite:///./booking.db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

class Base(Declarative_base):
    pass