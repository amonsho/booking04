from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import relationship
from .conf import BaseModelClass

class Hotel (BaseModelClass):
    
    photo = Column(String,nullable=False)
    name = Column(String,nullable=False)
    city = Column(String,nullable=False)
    address= Column(String,nullable=False)
    description = Column(String)
    
    rooms = relationship("Room", back_populates='hotel')