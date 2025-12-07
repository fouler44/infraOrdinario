from flask import Flask
import os
from pathlib import Path
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

from routes.base import base_routes
from routes.players import player_routes
from routes.user import user_routes
from routes.match import match_routes

# ✅ Subir un nivel desde backend/ hacia la raíz
BASE_DIR = Path(__file__).resolve().parent.parent  # Backend-LOL-ProyectoMovil/
ENV_PATH = BASE_DIR / '.env'

print(ENV_PATH)

load_dotenv(dotenv_path=ENV_PATH)

def create_app():
    app = Flask(__name__)
    
    # Configuración JWT
    jwt_secret = os.getenv("JWT_SECRET")
    
    if not jwt_secret:
        raise RuntimeError("JWT_SECRET no está configurado en .env")
    
    app.config["JWT_SECRET_KEY"] = jwt_secret
    jwt = JWTManager(app)
    
    app.register_blueprint(base_routes, url_prefix="/")
    app.register_blueprint(player_routes, url_prefix="/players")
    app.register_blueprint(user_routes, url_prefix="/user")
    app.register_blueprint(match_routes, url_prefix="/matches")
    
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"App running on port {port}")
    print(f"JWT_SECRET cargado: {'✅' if os.getenv('JWT_SECRET') else '❌'}")
    app.run(host="0.0.0.0", port=port, debug=True)