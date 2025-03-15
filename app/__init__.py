from flask import Flask, request
from app.config import config
from app.extensions import db, jwt, bcrypt, cache, limiter
from flask_migrate import Migrate

def create_app():
    """ Inicializa e configura a aplicação Flask """
    app = Flask(__name__, static_folder="../static")

    # 🔹 Define o ambiente com um fallback seguro
    env = app.config.get("FLASK_ENV", "development")
    app.config.from_object(config.get(env, config["development"]))

    # 🔹 Configurações extras do JWT
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = False  # 🔥 Em produção, defina como True
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # 🔥 Pode ser ativado se necessário
    app.config["JWT_SECRET_KEY"] = "sua_chave_secreta_super_segura"

    # 🔹 Inicializa extensões
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    migrate = Migrate(app, db)

    # 🔹 Importando e Registrando os Blueprints
    from app.routes.auth import auth_bp
    from app.routes.objetos import objetos_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.main import main_bp
    from app.api.routes import api_bp

    # 🔹 Registrando os Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(objetos_bp, url_prefix="/api/objetos")  # ✅ Evita conflito com `api_bp`
    app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")  # ✅ Evita conflito com `api_bp`
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(api_bp, url_prefix="/api")

    # 🔹 Verificação Global Antes de Cada Requisição
    @app.before_request
    def before_request_func():
        """ Bloqueia requisições de origem desconhecida (opcional) """
        if request.method == "OPTIONS":
            return  # Permite requisições OPTIONS (CORS)
        
        # 🔥 Verificação de segurança: Apenas aceita requisições locais ou domínios permitidos
        allowed_origins = ["127.0.0.1", "localhost"]
        if request.host.split(":")[0] not in allowed_origins:
            return {"erro": "Acesso não autorizado."}, 403

    return app
