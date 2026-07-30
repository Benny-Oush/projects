"""Todos REST API blueprint.

Pure JSON in, pure JSON out — no templates. Each route maps one HTTP verb to a
CRUD operation and returns the status code that good REST hygiene (and the spec)
expects: 200 read, 201 created, 204 no-content, 400 bad request, 404 not found.
"""
from flask import Blueprint, jsonify, request, abort

from ..extensions import db
from ..models import Todo

# The url_prefix lives on the blueprint, so routes below are relative to it.
bp = Blueprint("todos", __name__, url_prefix="/api/todos")


@bp.get("")
def list_todos():
    """GET /api/todos -> 200, all todos ordered by priority then id."""
    # SQLAlchemy 2.x style: select() + session.scalars() rather than Query.all().
    todos = db.session.scalars(
        db.select(Todo).order_by(Todo.priority.desc(), Todo.id),
    ).all()
    return jsonify([t.to_dict() for t in todos]), 200


@bp.post("")
def create_todo():
    """POST /api/todos -> 201 created, or 400 if title is missing/empty."""
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        abort(400, description="title is required and must be non-empty")

    priority = data.get("priority")
    if priority is not None:
        try:
            priority = int(priority)
        except (TypeError, ValueError):
            abort(400, description="priority must be an integer")
        if priority < 0:
            abort(400, description="priority must be a non-negative integer")
    else:
        priority = 0

    todo = Todo(
        title=title,
        complete=bool(data.get("complete", False)),
        priority=priority,
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@bp.patch("/<int:todo_id>")
def update_todo(todo_id):
    """PATCH /api/todos/<id> -> 200 partial update, or 404 if not found."""
    # SQLAlchemy 2.x PK lookup — replaces the deprecated Query.get().
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        abort(404, description=f"todo {todo_id} not found")

    data = request.get_json(silent=True) or {}

    # Partial update: only touch fields the client actually sent.
    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            abort(400, description="title must be non-empty")
        todo.title = title

    if "complete" in data:
        todo.complete = bool(data["complete"])

    if "priority" in data:
        try:
            priority = int(data["priority"])
        except (TypeError, ValueError):
            abort(400, description="priority must be an integer")
        if priority < 0:
            abort(400, description="priority must be a non-negative integer")
        todo.priority = priority

    db.session.commit()
    return jsonify(todo.to_dict()), 200


@bp.delete("/<int:todo_id>")
def delete_todo(todo_id):
    """DELETE /api/todos/<id> -> 204 no content, or 404 if not found."""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        abort(404, description=f"todo {todo_id} not found")

    db.session.delete(todo)
    db.session.commit()
    # 204 responses carry no body.
    return "", 204
