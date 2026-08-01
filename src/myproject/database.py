from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 直接从 config 导入，不再自己加载 .env
from src.myproject.config import DATABASE_URL

# 如果 DATABASE_URL 未设置，可以通过 config 兜底
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)