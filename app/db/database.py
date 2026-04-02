from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import BASE_DIR

Base = declarative_base()
DB_PATH = BASE_DIR / "database.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine( SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from app.db.models import User, Progress
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.core.security import pwd_context
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            hashed_password = pwd_context.hash("123")
            admin_user = User(username="admin", email="admin@admin.com", password=hashed_password)
            db.add(admin_user)
            db.commit()
    except Exception as e:
        print(f"Error initializing default admin: {e}")
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

