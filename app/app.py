from fastapi import FastAPI, HTTPException
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
    conn.commit()
    conn.close()

def baseGetTableData(table, username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row

def getUser(username):
    return baseGetTableData("users", username)

def getProgress(username: str):
    return baseGetTableData("progress", username)

def create_progress(progress: SaveProgress):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO progress (username, cookies, totalCookies, cps, cursor_count, grandma_count, factory_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (progress.username, progress.cookies, progress.totalCookies, progress.cps, progress.cursor_count,
         progress.grandma_count, progress.factory_count)
    )
    conn.commit()
    conn.close()


def update_progress(progress: SaveProgress):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE progress SET cookies = ?, totalCookies = ?, cps = ?, cursor_count = ?, grandma_count = ?, factory_count = ? WHERE username = ?",
        (progress.cookies, progress.totalCookies, progress.cps, progress.cursor_count, progress.grandma_count,
         progress.factory_count, progress.username)
    )
    conn.commit()
    conn.close()




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
def login(user: Login_user):
    row = getUser(user.username)

    user_db_password = str(row["password"])

    if not row:
        raise HTTPException(status_code=404, detail="foydalanuvchi mavjud emas")
    if user_db_password != user.password:
        raise HTTPException(status_code=401, detail="parol to'g'ri emas")

    return {"login": "success "}

@app.get("/clicker", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/clicker.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/save_progress")
def save_progress(progress : SaveProgress):

    row = getProgress(progress.username)
    if not row:
        create_progress(progress)
    else:
        update_progress(progress)

    return {"msg": "progress saqlandi"}

@app.get("/load_progress/{username}")
def laod_progress(username: str):
    row = getProgress(username)
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
        "username": row["username"],
        "cookies": row["cookies"],
        "totalCookies": row["totalCookies"],
        "cps": row["cps"],
        "cursor_count": row["cursor_count"],
        "grandma_count": row["grandma_count"],
        "factory_count": row["factory_count"],
    }


@app.get("/rating", response_class=HTMLResponse)
def rating_page():
    with open(BASE_DIR/"frontend/rating.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/get_rating")
def get_rating():
    # df = ensure_progress_csv_exist()
    # if df.empty:
    #     return []
    #
    # df["totalCookies"] = pd.to_numeric(df["totalCookies"], errors="coerce").fillna(0)
    # df_sorted = df.sort_values(by="totalCookies", ascending=False)
    # top_players = df_sorted.head(10)
    #
    # result = top_players[["username", "totalCookies", "cps"]].to_dict(orient="records")
    # return result
    pass

@app.get("/get_rank/{username}")
def get_rank(username: str):
    # df = ensure_progress_csv_exist()
    # if df.empty:
    #     return {"rank": 0}
    #
    # df["totalCookies"] = pd.to_numeric(df["totalCookies"], errors="coerce").fillna(0)
    # df_sorted = df.sort_values(by="totalCookies", ascending=False).reset_index(drop=True)
    #
    # user_row = df_sorted[df_sorted["username"] == username]
    # if not user_row.empty:
    #     rank = int(user_row.index[0]) + 1
    #     return {"rank": rank}

    return {"rank": 0}
