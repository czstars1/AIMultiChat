from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from pk_002.dependencies.database import get_db
from pk_002.models.db_models import User

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    """
    从 Authorization: Bearer <token> 中提取 token，
    并检查该 token 是否存在于 users 表中。
    若存在，返回 token 字符串；否则抛出 403。
    """
    token = credentials.credentials
    # 查询数据库，按 token 字段查找用户
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=403, detail="无效的访问令牌")
    # 返回 token（与之前 sessions.owner 存储的格式一致）
    return token
