import os
import urllib.parse
from dotenv import load_dotenv
from datetime import timedelta

# 🔹 Carrega o .env se necessário
if not os.getenv("DB_USER"):
    load_dotenv()

# 🔹 Função para construir a URI do banco de dados
def get_db_uri():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME")

    if user and password and db_name:
        password_encoded = urllib.parse.quote_plus(password, encoding="utf-8")  # 🔹 Adicionando encoding
        return f"postgresql://{user}:{password_encoded}@{host}/{db_name}"
    
    return "sqlite:///database.db"  # Fallback para SQLite

# 🔹 Configuração base
class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "chave_padrao_insegura")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "chave_jwt_padrao")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")
    print(f"📌 UPLOAD_FOLDER configurado para: {UPLOAD_FOLDER}")  # 🔹 Debug para conferir

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # 🔹 Configuração do JWT para uso com cookies
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False  # ❌ Apenas para desenvolvimento (defina como True em produção)
    JWT_COOKIE_HTTPONLY = True  # 🔒 Protege contra ataques XSS
    JWT_COOKIE_SAMESITE = "Lax"  # 🔹 Permite compartilhamento seguro
    JWT_COOKIE_CSRF_PROTECT = False  # ❌ Desativado temporariamente para testes (ative depois)

    # 🔹 Converte corretamente o tempo de expiração do JWT
    try:
        JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3)))  # ✅ Correção definitiva
    except ValueError:
        JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=3)  # Se houver erro, usa 3 horas como padrão

# 🔹 Configuração para Desenvolvimento
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_db_uri()

# 🔹 Configuração para Produção
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = get_db_uri()
    JWT_COOKIE_SECURE = True  # 🔒 Em produção, os cookies devem ser seguros

# 🔹 Configuração para Testes
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=1)  # 🔹 Tokens expiram rapidamente nos testes

# 🔹 Dicionário de Configurações
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}
