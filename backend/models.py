from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    video_url = Column(String)
    video_title = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    video_timestamp = Column(Float)
    role = Column(String)
    content = Column(String)
    created_at = Column(DateTime, server_default=func.now())