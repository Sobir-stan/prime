from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from pathlib import Path
from starlette.staticfiles import StaticFiles
from app.schemas import Body_test, New_user, Login_user, SaveProgress
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()
app.mount("/static/scripts", StaticFiles(directory=BASE_DIR/"frontend/scripts"), name="static")

@app.get("/product/{id}")
def login(id : int):
    print(id)
    return {"id": id}

@app.get("/product/")
def login(param : int):
    print(param)
    return {"param": param}

@app.post("/body_test")
def body_test(data : Body_test):
    print(data)
    return data

@app.post("/send")
def get_entered_data(text : dict):
    print(text)
    return {"text": text}

def get_csv_path():
    return BASE_DIR/"users.csv"

def get_progress_csv_path():
    return BASE_DIR/"progress.csv"

def ensure_progress_csv_exist():
    csv_path = get_progress_csv_path()
    print("111")
    if not csv_path.exists():
        df = pd.DataFrame(columns=("username","cookies", "totalCookies", "cps", "cursor", "grandma", "factory"))
        df.index.name = "id"
        df.to_csv(csv_path, index=True)

        return df
    else:
        return pd.read_csv(csv_path, index_col="id")


def ensure_csv_exist():
    csv_path = get_csv_path()

    if not csv_path.exists():
        df = pd.DataFrame(columns=("username", "email", "password"))
        df.index.name= "id"
        df.to_csv(csv_path, index=True)
        return df
    else:
        return pd.read_csv(csv_path, index_col="id")

def save_to_csv(user):

    error_msg = check_username(user.username, user.email)
    if error_msg:
        raise ValueError(error_msg)

    df = ensure_csv_exist()
    csv_path = get_csv_path()

    new_user_df = pd.DataFrame([user.model_dump()])
    updated_df = pd.concat([df, new_user_df],ignore_index=True)
    updated_df.index.name = "id"

    updated_df.to_csv(csv_path,index=True )

def check_username(username, email):
    df = ensure_csv_exist()
    if df.empty:
        return None

    if (df["username"] == username).any():
        return f"{username} nomli foydalanuvchi mavjud"
    elif (df["email"] == email).any():
        return f"{email} ishlatilgan"
    else:
        return None


@app.get("/register", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/register.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/register")
def register_user(user: New_user):
    save_to_csv(user)

    print(user.username, user.email, user.password)
    return {"msg": "ok "}

@app.get("/", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/login.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/")
def register_user(user: Login_user):
    df = ensure_csv_exist()

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

@app.get("/load_progress/{username}"):
def laod_progress(username: str):
    df = ensure_progress_csv_exist()
    user_row