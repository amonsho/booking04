from fastapi import FastAPI
from app.db.database import engine, Base
from app.models import user, room, booking

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Booking API"}