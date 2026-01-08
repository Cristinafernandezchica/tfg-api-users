from flask import Flask
from dotenv import load_dotenv
from config import Config
from src.database import db
from src.routes.auth_routes import auth_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5002)
