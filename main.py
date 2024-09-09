from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models import ToDoItem, SessionLocal

app = FastAPI()

class ToDoItemCreate(BaseModel):
    title: str
    description: str
    completed: bool = False

class ToDoItemResponse(ToDoItemCreate):
    id: int

    class Config:
        orm_mode = True

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/todos", response_model=List[ToDoItemResponse])
def read_todos(db: Session = Depends(get_db)):
    todos = db.query(ToDoItem).all()
    return todos

@app.post("/todos", response_model=ToDoItemResponse)
def create_todo(todo: ToDoItemCreate, db: Session = Depends(get_db)):
    db_todo = ToDoItem(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/todos/{id}", response_model=ToDoItemResponse)
def update_todo(id: int, todo: ToDoItemCreate, db: Session = Depends(get_db)):
    db_todo = db.query(ToDoItem).filter(ToDoItem.id == id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo item not found")
    
    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.completed = todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{id}")
def delete_todo(id: int, db: Session = Depends(get_db)):
    db_todo = db.query(ToDoItem).filter(ToDoItem.id == id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo item not found")
    
    db.delete(db_todo)
    db.commit()
    return {"detail": "ToDo item deleted"}
