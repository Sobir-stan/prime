from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import BASE_DIR
from datetime import datetime, timedelta

Base = declarative_base()
DB_PATH = BASE_DIR / "database.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine( SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from app.db.models import User, Progress, PromoCode
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


        promo_codes = ["muminov313", "_muminov.313", "ali313", "muminov", "313"]
        for code in promo_codes:
            if not db.query(PromoCode).filter(PromoCode.code == code).first():
                expires = datetime.utcnow() + timedelta(days=7)
                promo = PromoCode(code=code, expires_at=expires)
                db.add(promo)
        db.commit()
    except Exception as e:
        print(f"Error initializing default admin or promos: {e}")
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
