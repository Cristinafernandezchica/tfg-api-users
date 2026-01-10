from flask import Flask
from dotenv import load_dotenv
from config import Config
from src.database import db
from src.routes.auth_routes import auth_bp
from flask_migrate import Migrate

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5002)
