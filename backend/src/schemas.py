from pydantic import BaseModel

class TaskBase(BaseModel):
    name: str
    date: str
    complite: bool

class TaskCreate(TaskBase):
    id: int
    name: str
    date: str
    complite: bool

    class Config:
        from_attributes = True
        
class TaskOut(TaskCreate):
    pass 

