import asyncio
from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import engine, Base
from app.models import user, room, booking, hotel, messages, review, payment
from app.core.config import settings
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI()


@app.on_event("startup")
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Compatibility for existing SQLite DBs (no migrations yet).
        # If the table was created before adding columns in the model,
        # `create_all()` won't modify the schema and inserts will fail.
        if "sqlite" in str(engine.url):

            # ── ROOMS table migrations ──────────────────────────────────────
            res = await conn.execute(text("PRAGMA table_info(rooms);"))
            rows = res.fetchall()
            existing_cols = {r[1] for r in rows}

            if "is_available" not in existing_cols:
                await conn.execute(
                    text("ALTER TABLE rooms ADD COLUMN is_available BOOLEAN DEFAULT 1;")
                )
            if "photos" not in existing_cols:
                await conn.execute(text("ALTER TABLE rooms ADD COLUMN photos TEXT;"))
            # FIX: add is_deleted if missing (was not migrated before)
            if "is_deleted" not in existing_cols:
                await conn.execute(
                    text("ALTER TABLE rooms ADD COLUMN is_deleted BOOLEAN DEFAULT 0;")
                )

            # ── HOTELS table migrations ─────────────────────────────────────
            res = await conn.execute(text("PRAGMA table_info(hotels);"))
            rows = res.fetchall()
            hotel_cols = {r[1] for r in rows}

            # FIX: add is_deleted if missing
            if "is_deleted" not in hotel_cols:
                await conn.execute(
                    text("ALTER TABLE hotels ADD COLUMN is_deleted BOOLEAN DEFAULT 0;")
                )
            if "latitude" not in hotel_cols:
                await conn.execute(
                    text("ALTER TABLE hotels ADD COLUMN latitude REAL;")
                )
            if "longitude" not in hotel_cols:
                await conn.execute(
                    text("ALTER TABLE hotels ADD COLUMN longitude REAL;")
                )

            # ── MESSAGES table migrations ───────────────────────────────────
            res = await conn.execute(text("PRAGMA table_info(messages);"))
            rows = res.fetchall()
            msg_cols = {r[1] for r in rows}
            if "semder_id" in msg_cols:
                await conn.execute(
                    text("ALTER TABLE messages RENAME COLUMN semder_id TO sender_id;")
                )
            if "receiver_id" in msg_cols:
                await conn.execute(
                    text("ALTER TABLE messages RENAME COLUMN receiver_id TO chat_id;")
                )

            # ── USERS table migrations ──────────────────────────────────────
            res = await conn.execute(text("PRAGMA table_info(users);"))
            rows = res.fetchall()
            user_cols = {r[1] for r in rows}
            
            if "first_name" not in user_cols:
                await conn.execute(text("ALTER TABLE users ADD COLUMN first_name TEXT;"))
            if "last_name" not in user_cols:
                await conn.execute(text("ALTER TABLE users ADD COLUMN last_name TEXT;"))
            if "phone" not in user_cols:
                await conn.execute(text("ALTER TABLE users ADD COLUMN phone TEXT;"))


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
        "http://192.168.1.107:3000",
        "http://192.168.1.108:3000",
        "http://192.168.1.109:3000",
        "http://192.168.1.110:3000",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

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
