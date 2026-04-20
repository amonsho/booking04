from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import relationship
from .conf import BaseModelClass


class Messages(BaseModelClass):
    
    __tablename__ = 'messages'
    
    sender_id = Column(Integer)
    chat_id = Column(Integer)
    text = Column(String)
    
    
    