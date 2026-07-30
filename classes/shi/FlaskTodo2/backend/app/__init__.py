"""Application factory.

``create_app`` builds and configures a Flask app for a given environment.
Constructing the app inside a function (instead of a module-level global) lets
us create differently-configured apps for dev, prod, and the test suite, and it
sidesteps the import cycles a global ``app`` object tends to cause.
"""
import os

from flask import Flask, jsonify
from sqlalchemy import inspect, text

from .config import config_map
from .extensions import db, migrate, cors


def create_app(config_name=None):
    # Resolve which config to load: explicit arg > FLASK_CONFIG env var > "dev".
    config_name = config_name or os.getenv("FLASK_CONFIG", "dev")

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Preserve the field order of our to_dict() payloads instead of alphabetizing.
    app.json.sort_keys = False

    # Bind the shared extension instances to *this* app.
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # Import models after db.init_app so Flask-Migrate's autogenerate can see
    # them — done here rather than at top level to avoid an import cycle.
    from . import models  # noqa: F401

    # Create tables that don't exist yet (idempotent — safe on every restart).
    with app.app_context():
        db.create_all()
        inspector = inspect(db.engine)
        if inspector.has_table("todo"):
            columns = [column["name"] for column in inspector.get_columns("todo")]
            if "priority" not in columns:
                db.session.execute(
                    text(
                        "ALTER TABLE todo ADD COLUMN priority INTEGER NOT NULL DEFAULT 0",
                    ),
                )
                db.session.commit()

    # Register the JSON API blueprint (URL prefix lives on the blueprint).
    from .api.todos import bp as todos_bp
    app.register_blueprint(todos_bp)

    # Root index: a friendly JSON pointer to the API, so hitting the backend at
    # "/" returns something useful instead of the 404 handler. (The real UI is
    # served by the frontend, not here.)
    @app.get("/")
    def index():
        return {
            "service": "todo-api",
            "endpoints": {
                "health": "/health",
                "todos": "/api/todos",
            },
        }

    # Liveness probe used by the docker-compose healthcheck / load balancers.
    @app.get("/health")
    def health():
        return {"status": "ok"}

    _register_error_handlers(app)
    return app


def _register_error_handlers(app):
    """Return JSON (not Flask's default HTML page) for the errors the API raises."""

    @app.errorhandler(400)
    def bad_request(err):
        return jsonify(error="bad request", message=_describe(err)), 400

    @app.errorhandler(404)
    def not_found(err):
        return jsonify(error="not found", message=_describe(err)), 404


def _describe(err):
    # werkzeug HTTPExceptions carry a human-readable `.description`.
    return getattr(err, "description", str(err))
