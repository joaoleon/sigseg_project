from app.extensions import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash

# 📌 Lista todos os usuários
def listar_usuarios():
    try:
        usuarios = Usuario.query.all()
        return [{"id": u.id, "nome": u.nome, "email": u.email}], 200
    except Exception as e:
        return {"erro": "Erro ao listar usuários", "detalhe": str(e)}, 500

# 📌 Cria um novo usuário
def criar_usuario(data):
    if not data or not all(k in data for k in ["nome", "email", "senha"]):
        return {"erro": "Campos obrigatórios faltando"}, 400

    try:
        senha_hash = generate_password_hash(data["senha"])
        novo_usuario = Usuario(nome=data["nome"], email=data["email"], senha_hash=senha_hash)

        db.session.add(novo_usuario)
        db.session.commit()

        return {"id": novo_usuario.id, "nome": novo_usuario.nome, "email": novo_usuario.email}, 201
    except Exception as e:
        db.session.rollback()
        return {"erro": "Erro ao criar usuário", "detalhe": str(e)}, 500
