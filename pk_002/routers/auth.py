from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from pk_002.dependencies.database import get_db
from pk_002.models.request import UserRegister, UserLogin
from pk_002.services.auth import user_register_service, user_login_service

router=APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register",)
async def register_endpoint(request: UserRegister,db:Session =Depends(get_db)):
    user=user_register_service(db,request)
    return {"username":user.username,"token":user.token}

@router.post("/login",)
async def login_endpoint(request: UserLogin,db:Session = Depends(get_db)):
    token=user_login_service(db,request)
    return {"token:":token}

