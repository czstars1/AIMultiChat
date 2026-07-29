import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

if not os.getenv("DATABASE_URL"):
    env_file = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_file)

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:你的密码@localhost:3306/ai_chat_app")

engine=create_engine(DATABASE_URL,echo=False)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

def init_db():

    Base.metadata.create_all(bind=engine)