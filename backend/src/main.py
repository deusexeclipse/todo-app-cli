from fastapi import FastAPI, HTTPException,Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Optional, List
from schemas import TaskOut,TaskCreate
from models import Task
from database import engine, session_local, Base


app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

@app.get("/todo/ping")
async def ping():
    return "сервер работает"


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

@app.get("/todo/status")
async def check_task(id: Optional[int] = None, db: Session = Depends(get_db)):
    if id is None:
        return {"error": "id не передан"}
    task = db.query(Task).get(id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.complite = True
    db.commit()
    return "статус задачи обновлен"