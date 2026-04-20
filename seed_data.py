import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add current directory to path so we can import 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.models.hotel import Hotel
from app.models.room import Room
from app.models.review import Review
from app.models.booking import Booking
from app.models.user import User
from app.core.config import settings
from app.db.database import Base

async def seed():
    # Use the database URL from settings
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create Hotels
        hotel1 = Hotel(
            name="The Grand Alpine Sanctuary",
            country="Switzerland",
            city="Zermatt",
            address="Bahnhofstrasse 50, 3920 Zermatt",
            description="Experience ultimate luxury in the heart of the Swiss Alps. Our sanctuary offers unparalleled Matterhorn views, world-class spa facilities, and Michelin-star dining.",
            latitude=46.0207,
            longitude=7.7491,
            photo="media/resorts/alpine_hotel.png"
        )

        hotel2 = Hotel(
            name="Ocean Breeze Villas Bali",
            country="Indonesia",
            city="Bali",
            address="Jalan Raya Uluwatu, Pecatu, South Kuta, Bali",
            description="Escape to a tropical paradise. Private villas perched on limestone cliffs overlooking the Indian Ocean. Perfect for world-class surfing, stunning sunsets, and ultimate serenity.",
            latitude=-8.8149,
            longitude=115.0884,
            photo="media/resorts/ocean_hotel.png"
        )

        session.add_all([hotel1, hotel2])
        await session.commit()
        await session.refresh(hotel1)
        await session.refresh(hotel2)

        # Create Rooms for Alpine
        room1 = Room(
            hotel_id=hotel1.id,
            room_type="Alpine Luxury Suite",
            number_room="101",
            price=850.0,
            wifi=True,
            photos="media/resorts/alpine_room.png;media/resorts/alpine_hotel.png",
            is_available=True
        )

        room2 = Room(
            hotel_id=hotel1.id,
            room_type="Panorama Double Room",
            number_room="102",
            price=450.0,
            wifi=True,
            photos="media/resorts/alpine_hotel.png",
            is_available=True
        )

        # Create Rooms for Bali
        room3 = Room(
            hotel_id=hotel2.id,
            room_type="Oceanfront Private Villa",
            number_room="V01",
            price=1200.0,
            wifi=True,
            photos="media/resorts/ocean_room.png;media/resorts/ocean_hotel.png",
            is_available=True
        )

        room4 = Room(
            hotel_id=hotel2.id,
            room_type="Garden Terrace Suite",
            number_room="G01",
            price=600.0,
            wifi=True,
            photos="media/resorts/ocean_hotel.png",
            is_available=True
        )

        session.add_all([room1, room2, room3, room4])
        await session.commit()
        print("Success: 2 Hotels and 4 Rooms seeded with premium images!")

if __name__ == "__main__":
    asyncio.run(seed())
