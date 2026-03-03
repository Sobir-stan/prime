from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from pathlib import Path
from starlette.staticfiles import StaticFiles
from app.database import init_db, get_db_connection
from app.schemas import Body_test, New_user, Login_user, SaveProgress


BASE_DIR = Path(__file__).resolve().parent.parent
init_db()

app = FastAPI()
app.mount("/static/scripts", StaticFiles(directory=BASE_DIR/"frontend/scripts"), name="static")


def save_user(user):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (user.username, user.email, user.password)
    )
    cursor.commit()
    cursor.close()


@app.get("/register", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/register.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/register")
def register_user(user: New_user):
    save_user(user)

    print(user.username, user.email, user.password)
    return {"msg": "ok "}

@app.get("/", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/login.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/")
def register_user(user: Login_user):


    if df.empty:
        return {"msg": "fayl mavjud emas"}

    user_row = df[df["username"] == user.username]
    if user_row.empty:
        raise HTTPException(status_code=404, detail="foydalanuvchi mavjud emas")

    user_row = user_row.iloc[0].to_dict()

    if str(user_row["password"]) != user.password:
        raise HTTPException(status_code=401, detail="parol to'g'ri emas")

    return {"login": "success "}


@app.get("/clicker", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/clicker.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/save_progress")
def save_progress(progress : SaveProgress):
    df = ensure_progress_csv_exist()
    csv_path = get_progress_csv_path()
    
    if progress.username in df["username"].values:
        indf = df[df["username"] == progress.username].index[0]
        
        for col, val in progress.model_dump().items():
            df.at[indf, col] = val
    else:
        new_row_df = pd.DataFrame([progress.model_dump()])
        df = pd.concat([df, new_row_df],ignore_index=True)
        df.index.name = "id"
        
    df.to_csv(csv_path, index=True)
    return {"msg": "progress saqlandi"}

@app.get("/load_progress/{username}")
def laod_progress(username: str):
    df = ensure_progress_csv_exist()
    user_row =df[df["username"] == username]
    if user_row.empty:

        return {
            "username": username,
            "cookies" : 0.0,
            "totalCookies" : 0.0,
            "cps" : 0.0,
            "cursor_count" : 0,
            "grandma_count" : 0,
            "factory_count" : 0,
        }

    return user_row.iloc[0].to_dict()

@app.get("/rating", response_class=HTMLResponse)
def rating_page():
    with open(BASE_DIR/"frontend/rating.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/get_rating")
def get_rating():
    df = ensure_progress_csv_exist()
    if df.empty:
        return []

    df["totalCookies"] = pd.to_numeric(df["totalCookies"], errors="coerce").fillna(0)
    df_sorted = df.sort_values(by="totalCookies", ascending=False)
    top_players = df_sorted.head(10)

    result = top_players[["username", "totalCookies", "cps"]].to_dict(orient="records")
    return result

@app.get("/get_rank/{username}")
def get_rank(username: str):
    df = ensure_progress_csv_exist()
    if df.empty:
        return {"rank": 0}

    df["totalCookies"] = pd.to_numeric(df["totalCookies"], errors="coerce").fillna(0)
    df_sorted = df.sort_values(by="totalCookies", ascending=False).reset_index(drop=True)

    user_row = df_sorted[df_sorted["username"] == username]
    if not user_row.empty:
        rank = int(user_row.index[0]) + 1
        return {"rank": rank}

    return {"rank": 0}
