import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship

from pk_002.database import Base
from datetime import datetime

class User(Base):
    __tablename__="user"

    id=Column(String(36),primary_key=True,default=lambda: str(uuid.uuid4()))
    username=Column(String(50),unique=True,nullable=False)
    password=Column(String(250),nullable=False)
    token=Column(String(100),unique=True,nullable=False)
    created_at=Column(DateTime,default=datetime.now)

class Session(Base):
    __tablename__="sessions"

    id=Column(String(36),primary_key=True,default=lambda: str(uuid.uuid4()))
    name=Column(String(100),nullable=False)
    owner=Column(String(100),nullable=False,index=True)
    created_at=Column(DateTime,default=datetime.now)

    messages=relationship("Message",back_populates="session",cascade="all,delete-orphan")

class Message(Base):
    __tablename__="messages"

    id=Column(String(36),primary_key=True,default=lambda: str(uuid.uuid4()))
    session_id=Column(String(36),ForeignKey("sessions.id",ondelete="CASCADE"),nullable=False)
    role=Column(SAEnum("user","assistant",name="message_role"),nullable=False)
    content=Column(Text,nullable=False)
    created_at=Column(DateTime,default=datetime.now)

    session=relationship("Session",back_populates="messages")

