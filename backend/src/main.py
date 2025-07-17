from fastapi import FastAPI, HTTPException,Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from typing import Optional
from schemas import TaskCreate
from models import Task, User
from database import engine, session_local, Base
from authorize import check_password, hash_password
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import Annotated
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from jose import jwt, JWTError


app = FastAPI()
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=24*60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str):


@app.get("/todo/ping")
async def ping():
    return "сервер работает"

@app.post("todo/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == form_data.username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    user = User(
        username=form_data.username,
        hashed_password=hash_password(form_data.password)
    )
    db.add(user)
    db.commit()
    return {"msg": "User registered successfully"}
    
@app.post("todo/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
    
@app.get("/todo/get/all", response_model=dict)
async def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    good = [TaskCreate.model_validate(task) for task in tasks if task.complite]
    bad = [TaskCreate.model_validate(task) for task in tasks if not task.complite]

    return {
        "complite": good,
        "incomplite": bad
    }
    
@app.get("/todo/create/{name}")
async def create_task(name: str, db: Session = Depends(get_db)):
    new_task = Task(
        name=name, 
        date=f'{datetime.now().day}-{datetime.now().month}',
        complite=False
        )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return f"New task created successfully. ID - {len(db.query(Task).all())}"

@app.get("/todo/get")
async def get_task(id: Optional[int] = None, db: Session = Depends(get_db)):
    if id is None:
        return {"error": "id не передан"}
    task = db.query(Task).filter(Task.id == id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/todo/delete")
async def delete_task(id: Optional[int] = None, db: Session = Depends(get_db)):
    if id is None:
        return {"error": "id не передан"}
    task = db.query(Task).filter(Task.id == id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return "задача удалена"

@app.get("/todo/check")
async def check_task(id: Optional[int] = None, db: Session = Depends(get_db)):
    if id is None:
        return {"error": "id не передан"}
    task = db.query(Task).get(id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.complite = True
    db.commit()
    return "статус задачи обновлен"