import asyncio
from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import engine, Base
from app.models import user, room, booking
from app.api.hotel_router import hotel_router
from app.models import user, room, booking, hotel


app = FastAPI()

@app.on_event("startup")
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Compatibility for existing SQLite DBs (no migrations yet).
        # If the table was created before adding columns in the model,
        # `create_all()` won't modify the schema and inserts will fail.
        if "sqlite" in str(engine.url):
            res = await conn.execute(text("PRAGMA table_info(bookings);"))
            rows = res.fetchall()
            existing_cols = {r[1] for r in rows}  # PRAGMA: (cid, name, type, ...)
            if "is_available" not in existing_cols:
                await conn.execute(
                    text(
                        "ALTER TABLE bookings ADD COLUMN is_available BOOLEAN DEFAULT 0;"
                    )
                )

# -0-0-0-0--9--0-0-0-API AMONSHO -0-0-0-0-0-0

from app.api.auth_router import router as auth_router
from app.api.user_router import router as user_router
from app.api.profile_router import router as profile_router
from app.api.admin_router import router as admin_router
from app.api.review_router import router as review_router
from app.auth.google import router as google_router

from fastapi.staticfiles import StaticFiles
app.mount("/media", StaticFiles(directory="media"), name="media")
# app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")

from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie="session",
    same_site="lax",
    https_only=False,
)

# Allow frontend (localhost) to access API during development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL or "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(profile_router)
app.include_router(admin_router)
app.include_router(review_router)
app.include_router(google_router)

# -0-0-0-0--9--0-0-0-API ROMA -0-0-0-0-0-0
from app.api.hotel_router import hotel_router
from app.api.room_router import room_router
from app.api.booking_router import booking_router as b_r
from app.api.ai_router import router as ai_router
app.include_router(hotel_router)
app.include_router(room_router)
app.include_router(b_r)
app.include_router(ai_router)






