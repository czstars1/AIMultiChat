import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.myproject.models.request import UserRegister, UserLogin
from src.myproject.models.db_models import User as UserModel


def user_register_service(db:Session ,request:UserRegister):
    exiting=db.query(UserModel).filter(UserModel.username == request.name).first()
    if exiting:
        raise HTTPException(status_code=400,detail="名称重复")
    user=UserModel(
        id = uuid.uuid4(),
        username=request.name,
        password=request.password,
        token=str(uuid.uuid4()),
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def user_login_service(db:Session ,request:UserLogin):
    print(f"【调试】收到的 name: {request.name}")  
    exiting=db.query(UserModel).filter(UserModel.username == request.name).first()
    if not exiting:
        raise HTTPException(status_code=401,detail="不存在此用户")
    print(f"【调试】数据库中的密码: {exiting.password}")   # 看存的是什么
    print(f"【调试】收到的密码明文: {request.password}")    # 看前端传了什么
    if exiting.password != request.password:
        raise HTTPException(status_code=401,detail="密码错误")

    return exiting.token

