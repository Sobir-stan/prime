from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import BASE_DIR

Base = declarative_base()

DB_PATH = BASE_DIR / "database.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    from app.db.models import User, Progress, Skin, UserSkin
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # text() wrapper bilan to'g'ri ishlaydi
        res = db.execute(text("PRAGMA table_info('skins')")).fetchall()
        cols = [r[1] for r in res]
        if 'type' not in cols:
            db.execute(text("ALTER TABLE skins ADD COLUMN type TEXT"))
            db.commit()
    except Exception as e:
        print(f"Migration error: {e}")

    try:
        from app.core.security import pwd_context
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            hashed_password = pwd_context.hash("123")
            admin_user = User(username="admin", email="admin@admin.com", password=hashed_password)
            db.add(admin_user)
            db.commit()

        from app.db.models import Progress, Skin
        existing_progress = db.query(Progress).filter_by(username=admin_user.username).first()
        if not existing_progress:
            prog = Progress(username=admin_user.username, cookies=30.12, totalCookies=30.12, cps=0.0,
                            cursor_count=0, grandma_count=0, factory_count=0)
            db.add(prog)
            db.commit()

        skins_count = db.query(Skin).count()
        if skins_count == 0:
            default_skins = [
                Skin(name='Cookie', price=0.0, description='Default cookie skin', rarity='common', image=None,
                     type='cookie'),
                Skin(name='Egg', price=50.0, description='Egg skin', rarity='uncommon', image=None, type='egg'),
                Skin(name='Orange', price=100.0, description='Orange skin', rarity='rare', image=None, type='orange'),
                Skin(name='Coin', price=200.0, description='Coin skin', rarity='epic', image=None, type='coin'),
            ]
            db.add_all(default_skins)
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