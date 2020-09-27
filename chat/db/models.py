from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from chat.db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer, unique=True, index=True, primary_key=True, autoincrement=True
    )
    username = Column(String, unique=True)
    password = Column(String)

    messages = relationship("Message", back_populates="owner")


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(
        Integer, unique=True, index=True, primary_key=True, autoincrement=True
    )
    message = Column(String)
    date_time = Column(DateTime)

    owner_id = Column(Integer, ForeignKey("users.user_id"))
    owner = relationship("User", back_populates="messages")
