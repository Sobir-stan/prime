# Ushbu fayl ma'lumotlar bazasiga ulanishni va uni boshqarishni amalga oshiradi.
# SQLAlchemy orqali bazaga ulanish yo'llari va boshlang'ich sozlamalar qilinadi.
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import BASE_DIR

# Modellar yaratish uchun asosiy klass
Base = declarative_base()

# SQLite bazasining fayl manzilini saqlash
DB_PATH = BASE_DIR / "database.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Baza bilan bog'lanish obyektini yaratish
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Har bir so'rov uchun alohida sessiya yaratish uchun klass
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ma'lumotlar bazasini dastlabki ishga tushiruvchi funksiya
def init_db():
    from app.db.models import User, Progress
    # Barcha modellar asosida jadvallarni yaratish
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.core.security import pwd_context
        # Default admin foydalanuvchi borligini tekshirish
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # Agar yo'q bo'lsa, yangi admin yaratish
            hashed_password = pwd_context.hash("123")
            admin_user = User(username="admin", email="admin@admin.com", password=hashed_password)
            db.add(admin_user)
            db.commit()
    except Exception as e:
        print(f"Error initializing default admin: {e}")
    finally:
        # Sessiyani albatta yopish
        db.close()

# API marshrutlari uchun sessiyani ochib beradigan generator funksiya
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # So'rov yakunlangach sessiyani yopish
        db.close()
