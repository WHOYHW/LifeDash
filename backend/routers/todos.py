from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date, time

from database import get_db
from models import User, Todo
from schemas import TodoCreateRequest, TodoUpdateRequest, TodoResponse, ApiResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/api/todos", tags=["待办"])


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    request: TodoCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_todo = Todo(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        due_date=request.due_date,
        tag=request.tag,
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return ApiResponse(
        code=200,
        message="创建成功",
        data=TodoResponse.model_validate(new_todo).model_dump(),
    )


@router.get("", response_model=ApiResponse)
def list_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = Query("all", alias="status"),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    tag: Optional[str] = None,
):
    query = db.query(Todo).filter(Todo.user_id == current_user.id)

    if status_filter == "active":
        query = query.filter(Todo.is_completed == False)
    elif status_filter == "completed":
        query = query.filter(Todo.is_completed == True)
    elif status_filter == "overdue":
        now = datetime.now()
        query = query.filter(
            Todo.is_completed == False,
            Todo.due_date.isnot(None),
            Todo.due_date < now,
        )
    elif status_filter == "today":
        today_start = datetime.combine(date.today(), time.min)
        today_end = datetime.combine(date.today(), time(23, 59, 59))
        query = query.filter(
            Todo.is_completed == False,
            Todo.due_date.isnot(None),
            Todo.due_date >= today_start,
            Todo.due_date <= today_end,
        )

    if tag:
        query = query.filter(Todo.tag == tag)

    if sort_order == "asc":
        query = query.order_by(Todo.created_at.asc())
    else:
        query = query.order_by(Todo.created_at.desc())

    todos = query.all()
    return ApiResponse(
        code=200,
        message="success",
        data=[TodoResponse.model_validate(t).model_dump() for t in todos],
    )


@router.get("/today", response_model=ApiResponse)
def get_today_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now()
    today = date.today()
    todos = db.query(Todo).filter(
        Todo.user_id == current_user.id,
        Todo.is_completed == False,
    ).order_by(Todo.created_at.desc()).all()

    today_todos = [
        t for t in todos
        if t.due_date is None
        or (t.due_date.date() == today and t.due_date >= now)
        or (t.due_date.date() < today)
    ]

    return ApiResponse(
        code=200,
        message="success",
        data=[TodoResponse.model_validate(t).model_dump() for t in today_todos],
    )


@router.get("/{todo_id}", response_model=ApiResponse)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(
        Todo.id == todo_id, Todo.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办不存在")
    return ApiResponse(
        code=200,
        message="success",
        data=TodoResponse.model_validate(todo).model_dump(),
    )


@router.put("/{todo_id}", response_model=ApiResponse)
def update_todo(
    todo_id: int,
    request: TodoUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(
        Todo.id == todo_id, Todo.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办不存在")

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)

    db.commit()
    db.refresh(todo)
    return ApiResponse(
        code=200,
        message="更新成功",
        data=TodoResponse.model_validate(todo).model_dump(),
    )


@router.patch("/{todo_id}/toggle", response_model=ApiResponse)
def toggle_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(
        Todo.id == todo_id, Todo.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办不存在")

    todo.is_completed = not todo.is_completed
    db.commit()
    db.refresh(todo)
    return ApiResponse(
        code=200,
        message="操作成功",
        data=TodoResponse.model_validate(todo).model_dump(),
    )


@router.delete("/{todo_id}", response_model=ApiResponse)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    todo = db.query(Todo).filter(
        Todo.id == todo_id, Todo.user_id == current_user.id
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办不存在")

    db.delete(todo)
    db.commit()
    return ApiResponse(code=200, message="删除成功", data=None)
