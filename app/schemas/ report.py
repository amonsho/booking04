# from sqlalchemy import select,func
# from app.models.hotel import Hotel
# from app.models.room import Room

# class ReportService: 
    
#     def __init__(self,db):
#         self.db = db 
        
#     async def get_hotel_report(self):
#         tottal_hotels_result = await self.db.execute(
#             select(func.count(Hotel.id))
#         )
        
#         total_hotels = total_hotels_result.scalar()
