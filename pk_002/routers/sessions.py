from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pk_002.dependencies.auth import verify_token
from pk_002.dependencies.database import get_db
from pk_002.models.request import SessionCreate, SessionUpdate
from pk_002.services import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("",status_code=201)
async def create_new_session1(request: SessionCreate,user_id: str = Depends(verify_token),db: Session = Depends(get_db)):
    session = session_service.create_session(db, request.name, user_id)
    return {
        "id": session.id,
        "name": session.name,
        "created_at": session.created_at
    }

@router.get("")
async def get_all_sessions1(db:Session = Depends(get_db),token: str = Depends(verify_token)):
    sessions = session_service.get_sessions_by_owner(db, token)
    return [
        {
            "id": s.id,
            "name": s.name,
            "created_at": s.created_at
        }
        for s in sessions
    ]

@router.get("/{session_id}")
async def get_session1(session_id: str,token: str = Depends(verify_token),db: Session = Depends(get_db)):
    session = session_service.get_session_by_id(db,session_id, token)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": session.id,
        "name": session.name,
        "created_at": session.created_at
    }

@router.put("/{session_id}")
async def update_session1(session_id: str, request: SessionUpdate,token: str = Depends(verify_token),db:Session = Depends(get_db)):
    update_session = session_service.update_session(db,session_id,request.name,token)
    if not update_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": update_session.id,
        "name": update_session.name,
        "created_at": update_session.created_at
    }

@router.delete("/{session_id}")
async def delete_session1(session_id: str,token: str = Depends(verify_token),db:Session = Depends(get_db)):
    if not session_service.delete_session(db,session_id, token):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"OK":True}


