from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.db.database import init_db
from app.routers import rating

init_db()

app = FastAPI()

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

app.include_router(login.router)
app.include_router(register.router)
app.include_router(clicker.router)
app.include_router(rating.router)





BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()




def check_username(username, email, db: Session):

    if db.query(User).filter(User.username == username).first():
        return f"{username} nomli foydalanuvchi mavjud"

    if db.query(User).filter(User.email == email).first():
        return f"{email} ishlatilgan email"

    return None


@app.get("/register", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/register.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/register")
def register_user(user: New_user, db:Session = Depends(get_db)):
    try:
        save_user(user, db)
        print(user.username, user.email, user.password)
        return {"msg": "ok "}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/login.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/")
def login(user: Login_user, response: Response, db : Session = Depends(get_db)):
    row = db.query(User).filter(User.username == user.username).first()

    if not row:
        raise HTTPException(status_code=404, detail="foydalanuvchi mavjud emas")
    if not pwd_context.verify(user.password, str(row.password)):
        raise HTTPException(status_code=401, detail="parol to'g'ri emas")

    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {"login": "success "}


@app.get("/clicker", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/clicker.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/save_progress")
def save_progress(progress : SaveProgress, db : Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    if current_user != progress.username:
        raise HTTPException(status_code=403, detail="Ruxsat etilmagan")

    db_progress = db.query(Progress).filter(Progress.username == progress.username).first()

    if not db_progress:
        new_progress = Progress(
            username=progress.username,
            cookies=progress.cookies,
            totalCookies=progress.totalCookies,
            cps=progress.cps,
            cursor_count=progress.cursor_count,
            grandma_count=progress.grandma_count,
            factory_count=progress.factory_count
        )
        db.add(new_progress)
    else:
        db_progress.cookies = progress.cookies
        db_progress.totalCookies = progress.totalCookies
        db_progress.cps = progress.cps
        db_progress.cursor_count = progress.cursor_count
        db_progress.grandma_count = progress.grandma_count
        db_progress.factory_count = progress.factory_count

    db.commit()
    return {"msg": "progress saqlandi"}

@app.get("/load_progress/{username}")
def laod_progress(username: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    if current_user != username:
        raise HTTPException(status_code=403, detail="Ruxsat etilmagan")

    row = db.query(Progress).filter(Progress.username == username).first()
    if not row:
        return {
                "username": username,
                "cookies" : 0.0,
                "totalCookies" : 0.0,
                "cps" : 0.0,
                "cursor_count" : 0,
                "grandma_count" : 0,
                "factory_count" : 0,
            }
    return {
        "username": row.username,
        "cookies" : row.cookies,
        "totalCookies" : row.totalCookies,
        "cps" : row.cps,
        "cursor_count" : row.cursor_count,
        "grandma_count" : row.grandma_count,
        "factory_count" : row.factory_count,
    }




@app.get("/get_rating")
def get_rating(db: Session = Depends(get_db)):
    top_progress = db.query(Progress).order_by(Progress.totalCookies.desc()).limit(10).all()
    result= []
    for p in top_progress:
        result.append({
            "username": p.username,
            "totalCookies": p.totalCookies,
            "cps": p.cps
        })
    return result

@app.get("/get_rank/{username}")
def get_rank(username: str, db: Session = Depends(get_db)):
    db_progrerss =  db.query(Progress).filter(Progress.username == username).first()

    if not db_progrerss:
        return {"rank": 0}

    user_score = db_progrerss.totalCookies
    rank_ahead = db.query(Progress).filter(Progress.totalCookies > user_score).count()

    return {"rank": rank_ahead + 1}