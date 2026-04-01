from sqlalchemy.orm import Session
from app.db.models import User, Progress
from app.schemas import New_user, Login_user, SaveProgress
from app.core.security import pwd_context

def get_by_username(db : Session , username: str):
    return  db.query(User).filter(User.username == username).first()

def get_user_by_email(db : Session , email: str):
    return  db.query(User).filter(User.email == email).first()

def create_user(user: New_user, db: Session):
    hashed_password = pwd_context.hash(user.password)

    new_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# get_progress_by_username(db, username) => Progress
# create_or_update_progress(db, progress) => Progress
# get_top_progress(db, limit) => List[Progress]
# get_progress_rank(db, username) => int