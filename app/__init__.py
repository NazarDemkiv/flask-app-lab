from pathlib import Path

from flask import Flask, render_template

from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .extensions import db, migrate, session


CONFIGURATIONS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def create_app(config_name: str = "development") -> Flask:
    """Create and configure a Flask application instance."""
    if config_name not in CONFIGURATIONS:
        raise ValueError(
            f"Unknown configuration: {config_name!r}. "
            f"Choose one of: {', '.join(CONFIGURATIONS)}."
        )

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(CONFIGURATIONS[config_name])
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    if app.config.get("SERVER_SIDE_SESSIONS", False):
        app.config.setdefault(
            "SESSION_FILE_DIR", str(Path(app.instance_path) / "flask_session")
        )
        session.init_app(app)

    from .posts.models import Post 
    from .products.models import Product

    migrate.init_app(app, db)

    from .users import user_bp
    from .products import product_bp
    from .posts import post_bp
    from .views import register_main_routes

    register_main_routes(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(post_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    return app
