import uuid
from sqlalchemy.orm import Session
from src.myproject.models.db_models import Session as SessionModel


def create_session(db:Session,name:str,owner:str):
    session=SessionModel(
        id=str(uuid.uuid4()),
        name=name,
        owner=owner,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_sessions_by_owner(db:Session,owner:str):
    return db.query(SessionModel).filter(SessionModel.owner==owner).all()

def get_session_by_id(db:Session,session_id:str,owner:str):
    return db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.owner == owner
    ).first()

def delete_session(db:Session,session_id:str,owner:str):
    session=get_session_by_id(db,session_id,owner)
    if session:
        db.delete(session)
        db.commit()
        return {"OK":True}
    return None

def update_session(db:Session,session_id:str,request:str,owner:str):
    session=get_session_by_id(db,session_id,owner)
    if session:
        session.name = request
        db.commit()
        db.refresh(session)
        return session
    return None

# fake_db : dict[str, SessionResponse] = {
#     "session-001":
#         SessionResponse(
#             id="session-001",
#             name="我的第一个会话",
#             created_at=datetime(2026, 7, 1),
#             owner="alice"
#         ),
#     "session-002":
#         SessionResponse(
#             id="session-002",
#             name="技术讨论",
#             created_at=datetime(2026, 7, 2),
#             owner="bob"
#         ),
# }
#
# def create_session(session: SessionCreate,user_id:str):
#     session_id=str(uuid.uuid4())
#
#     new_session = SessionResponse(
#         id=session_id,
#         name=session.name,
#         owner=user_id,
#     )
#     fake_db[session_id]=new_session
#     return new_session
#
# def get_sessions():
#     return list(fake_db.values())
#
# def get_session(session_id:str,user_id:str):
#     if session_id not in fake_db:
#         raise HTTPException(
#             status_code=404,
#             detail="Session not found"
#         )
#     if fake_db[session_id].owner!=user_id:
#         raise HTTPException(
#             status_code=403,
#             detail="not your session"
#         )
#     return fake_db[session_id]
#
# def update_session(session_id:  str,session: SessionUpdate,user_id: str):
#     session1=fake_db.get(session_id)
#     if not session1 or session1.owner!=user_id:
#         raise HTTPException(
#             status_code=403,
#             detail="not your session"
#         )
#
#     session1.name=session.name
#
#     return session1
#
# def delete_session(session_id: str,user_id: str):
#     session1=fake_db.get(session_id)
#     if not session1 or session1.owner!=user_id:
#         raise HTTPException(
#             status_code=403,
#             detail="not your session"
#         )
#     del fake_db[session_id]
#     return {"OK":True}
#
#

