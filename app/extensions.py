from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

# 🔹 Criando instâncias únicas (não criar outra em outro lugar!)
db = SQLAlchemy()
cache = Cache()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
jwt = JWTManager()
bcrypt = Bcrypt()
