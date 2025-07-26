from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from datetime import datetime, date
import uvicorn

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Temporary storage for todos (in-memory)
todos: List[dict] = []

next_id = 1

def get_todo_by_id(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    return None

# GET - แสดงหน้าแรกพร้อม todo ทั้งหมด
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "todos": todos,
        "page_title": "Todo Application",
        "is_upcoming_page": False,
        "is_completed_page": False,
        "is_overdue_page": False
    })

# GET - API แสดง todo ทั้งหมด
@app.get("/api/todos")
def get_all_todos():
    return {
        "success": True,
        "data": todos,
        "count": len(todos)
    }

# GET - แสดงเฉพาะงานที่ยังไม่ครบกำหนด
@app.get("/api/todos/upcoming")
def get_upcoming_todos():
    today = date.today().isoformat()
    upcoming_todos = [
        todo for todo in todos 
        if not todo["completed"] and todo["due_date"] >= today
    ]
    return {
        "success": True,
        "data": upcoming_todos,
        "count": len(upcoming_todos)
    }

# GET - หน้าแสดงงานที่ยังไม่ครบกำหนด
@app.get("/upcoming", response_class=HTMLResponse)
def upcoming_todos_page(request: Request):
    today = date.today().isoformat()
    upcoming_todos = [
        todo for todo in todos 
        if not todo["completed"] and todo["due_date"] >= today
    ]
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "todos": upcoming_todos,
        "page_title": "งานที่ยังไม่ครบกำหนด",
        "is_upcoming_page": True,
        "is_completed_page": False,
        "is_overdue_page": False
    })

# GET - API แสดงงานที่เสร็จแล้ว
@app.get("/api/todos/completed")
def get_completed_todos():
    completed_todos = [todo for todo in todos if todo["completed"]]
    return {
        "success": True,
        "data": completed_todos,
        "count": len(completed_todos)
    }

# GET - หน้าแสดงงานที่เสร็จแล้ว
@app.get("/completed", response_class=HTMLResponse)
def completed_todos_page(request: Request):
    completed_todos = [todo for todo in todos if todo["completed"]]
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "todos": completed_todos,
        "page_title": "งานที่เสร็จแล้ว",
        "is_upcoming_page": False,
        "is_completed_page": True,
        "is_overdue_page": False
    })

# GET - API แสดงงานที่เกินกำหนด
@app.get("/api/todos/overdue")
def get_overdue_todos():
    today = date.today().isoformat()
    overdue_todos = [
        todo for todo in todos 
        if not todo["completed"] and todo["due_date"] < today
    ]
    return {
        "success": True,
        "data": overdue_todos,
        "count": len(overdue_todos)
    }

# GET - หน้าแสดงงานที่เกินกำหนด
@app.get("/overdue", response_class=HTMLResponse)
def overdue_todos_page(request: Request):
    today = date.today().isoformat()
    overdue_todos = [
        todo for todo in todos 
        if not todo["completed"] and todo["due_date"] < today
    ]
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "todos": overdue_todos,
        "page_title": "งานที่เกินกำหนด",
        "is_upcoming_page": False,
        "is_completed_page": False,
        "is_overdue_page": True
    })

# POST - เพิ่ม todo ใหม่
@app.post("/create-todo")
def create_todo(
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(...),
    completed: bool = Form(False)
):
    global next_id
    
    # Validate due_date format
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    new_todo = {
        "id": next_id,
        "title": title.strip(),
        "description": description.strip(),
        "due_date": due_date,
        "completed": completed,
        "created_at": datetime.now().isoformat()
    }
    
    todos.append(new_todo)
    next_id += 1
    
    return RedirectResponse("/", status_code=303)

# POST - API เพิ่ม todo ใหม่
@app.post("/api/todos")
def create_todo_api(
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(...),
    completed: bool = Form(False)
):
    global next_id
    
    # Validate due_date format
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    new_todo = {
        "id": next_id,
        "title": title.strip(),
        "description": description.strip(),
        "due_date": due_date,
        "completed": completed,
        "created_at": datetime.now().isoformat()
    }
    
    todos.append(new_todo)
    next_id += 1
    
    return {
        "success": True,
        "message": "Todo created successfully",
        "data": new_todo
    }

# PUT - แก้ไข todo
@app.put("/api/todos/{todo_id}")
def update_todo(
    todo_id: int,
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(...),
    completed: bool = Form(False)
):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Validate due_date format
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    todo["title"] = title.strip()
    todo["description"] = description.strip()
    todo["due_date"] = due_date
    todo["completed"] = completed
    
    return {
        "success": True,
        "message": "Todo updated successfully",
        "data": todo
    }

# POST - แก้ไข todo (สำหรับ HTML form)
@app.post("/update-todo/{todo_id}")
def update_todo_form(
    todo_id: int,
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(...),
    completed: bool = Form(False)
):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Validate due_date format
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    todo["title"] = title.strip()
    todo["description"] = description.strip()
    todo["due_date"] = due_date
    todo["completed"] = completed
    
    return RedirectResponse("/", status_code=303)

# DELETE - ลบ todo
@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todos.remove(todo)
    return {
        "success": True,
        "message": "Todo deleted successfully"
    }

# POST - ลบ todo (สำหรับ HTML form)
@app.post("/delete-todo/{todo_id}")
def delete_todo_form(todo_id: int):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todos.remove(todo)
    return RedirectResponse("/", status_code=303)

# POST - Toggle complete status
@app.post("/toggle-todo/{todo_id}")
def toggle_todo_complete(todo_id: int):
    todo = get_todo_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo["completed"] = not todo["completed"]
    return RedirectResponse("/", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)