"""Data models.

The ``Todo`` table is a *fixed contract* inherited from the original app:
table name ``todo`` with columns ``id`` / ``title`` / ``complete``. We keep that
shape exactly — this refactor changes structure, not the database.
"""
from .extensions import db


class Todo(db.Model):
    # Explicit table name that matches SQLAlchemy's default for the class `Todo`,
    # so we stay on the existing table rather than creating a new one.
    __tablename__ = "todo"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.Integer, default=1)

    def to_dict(self):
        """Serialize to the JSON shape the API and the frontend agree on."""
        return {
            "id": self.id,
            "title": self.title,
            "complete": self.complete,
            "priority": self.priority,
        }

    def __repr__(self):
        return f"<Todo {self.id} {self.title!r} complete={self.complete} priority={self.priority}>"
