from src.myproject.database import SessionLocal


async def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()