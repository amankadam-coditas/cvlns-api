from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.models import Base

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    ),
)

print("check 01", id(settings))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with all tables"""
    Base.metadata.create_all(bind=engine)
