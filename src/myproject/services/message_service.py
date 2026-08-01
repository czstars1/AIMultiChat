import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from src.myproject.models.db_models import Message

def add_message(db:Session,session_id:str,role:str,content:str):
    message=Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content,
        created_at=datetime.now()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_messages_by_session(db: Session, session_id: str, limit: int = 50):
    return db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(Message.created_at.asc()).limit(limit).all()