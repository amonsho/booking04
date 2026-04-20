import asyncio
from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import engine, Base
from app.models import user, room, booking
from app.api.hotel_router import hotel_router
<<<<<<< HEAD
from app.models import user, room, booking, hotel, messages, review, payment
=======
from app.models import user, room, booking, hotel
from app.core.config import settings
>>>>>>> 6cdf953d24a70c7f7cd3d438ab4f66be46e9d6d8


app = FastAPI()

@app.on_event("startup")
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Compatibility for existing SQLite DBs (no migrations yet).
        # If the table was created before adding columns in the model,
        # `create_all()` won't modify the schema and inserts will fail.
        if "sqlite" in str(engine.url):
            res = await conn.execute(text("PRAGMA table_info(rooms);"))
            rows = res.fetchall()
            existing_cols = {r[1] for r in rows}  # PRAGMA: (cid, name, type, ...)
            if "is_available" not in existing_cols:
                await conn.execute(
                    text(
                        "ALTER TABLE rooms ADD COLUMN is_available BOOLEAN DEFAULT 1;"
                    )
                )
<<<<<<< HEAD
            
            # Simple migration for messages table typos
            res = await conn.execute(text("PRAGMA table_info(messages);"))
            rows = res.fetchall()
            existing_cols = {r[1] for r in rows}
            if "semder_id" in existing_cols:
                await conn.execute(text("ALTER TABLE messages RENAME COLUMN semder_id TO sender_id;"))
            if "receiver_id" in existing_cols:
                await conn.execute(text("ALTER TABLE messages RENAME COLUMN receiver_id TO chat_id;"))
=======
            if "photos" not in existing_cols:
                await conn.execute(
                    text(
                        "ALTER TABLE rooms ADD COLUMN photos TEXT;"
                    )
                )
>>>>>>> 6cdf953d24a70c7f7cd3d438ab4f66be46e9d6d8

# -0-0-0-0--9--0-0-0-API AMONSHO -0-0-0-0-0-0

from app.api.auth_router import router as auth_router
from app.api.user_router import router as user_router
from app.api.profile_router import router as profile_router
from app.api.admin_router import router as admin_router
from app.api.review_router import router as review_router
from app.auth.google import router as google_router
from app.api.payment_router import router as payment_router

# Allow frontend (localhost) to access API during development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        settings.FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
app.mount("/media", StaticFiles(directory="media"), name="media")
# app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(profile_router)
app.include_router(admin_router)
app.include_router(review_router)
app.include_router(google_router)
app.include_router(payment_router)

# -0-0-0-0--9--0-0-0-API ROMA -0-0-0-0-0-0
from app.api.hotel_router import hotel_router
from app.api.room_router import room_router
from app.api.booking_router import booking_router as b_r
from app.api.ai_router import router as ai_router
from app.api.chat import chat_router
app.include_router(hotel_router)
app.include_router(room_router)
app.include_router(b_r)
app.include_router(ai_router)
app.include_router(chat_router)






