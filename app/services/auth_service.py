from datetime import timedelta
from flask import jsonify, make_response, current_app, session, request
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, get_jwt_identity
from app.extensions import db
from app.models.usuario import Usuario

# 📌 Cadastro de Usuário

def registrar_usuario(data):
    """Registra um novo usuário no banco de dados."""

    required_fields = ["nome", "email", "senha", "cpf"]
    for field in required_fields:
        if not data.get(field):
            return {"erro": f"O campo {field} é obrigatório."}, 400

    email = data["email"].strip().lower()
    cpf = data["cpf"].strip()

    # 🔹 Validação para evitar e-mails e CPFs duplicados
    if Usuario.query.filter_by(email=email).first():
        return {"erro": "E-mail já cadastrado"}, 409
    if Usuario.query.filter_by(cpf=cpf).first():
        return {"erro": "CPF já cadastrado"}, 409

    # 🔹 Criando um novo usuário
    novo_usuario = Usuario(
        nome=data["nome"].strip(),
        email=email,
        cpf=cpf,
        telefone=data.get("telefone"),
        data_nascimento=data.get("data_nascimento"),
        genero=data.get("genero"),
        cidade=data.get("cidade"),
        estado=data.get("estado")
    )

    # 🔥 Certifique-se de que a senha está sendo criptografada corretamente
    novo_usuario.set_senha(data["senha"])  

    db.session.add(novo_usuario)
    db.session.commit()

    return {"mensagem": "Usuário registrado com sucesso!", "redirect_url": "/auth/login"}, 201

# 📌 Login de Usuário
def login_usuario(data=None):
    # 🔍 Tenta capturar os dados da requisição
    data = request.get_json()  # Tenta capturar JSON
    if not data:
        data = request.form  # Se JSON for None, tenta capturar via formulário

    print(f"📌 request.get_json(): {request.get_json()}")
    print(f"📌 request.form: {request.form}")
    print(f"📌 request.data: {request.data}")  # Dados brutos recebidos
    print(f"📌 request.content_type: {request.content_type}")  # Tipo de conteúdo recebido

    print(f"📌 Dados recebidos no login: {data}")  # Debug final

    email = data.get("email", "").strip().lower()
    senha_digitada = data.get("senha", "").strip()

    print(f"📌 Tentando login com email: {email}")

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        print("❌ Erro: Usuário não encontrado!")
        return {"erro": "Usuário não encontrado."}, 401

    print(f"📌 Senha armazenada no banco para {usuario.email}: {usuario.senha}")

    if not usuario.verificar_senha(senha_digitada):
        print("❌ Erro: Senha incorreta!")
        return {"erro": "Senha incorreta."}, 401

    token = create_access_token(identity=str(usuario.id))

    session["user_id"] = usuario.id
    session.permanent = True

    response = make_response(jsonify({
        "mensagem": "Login realizado com sucesso!",
        "redirect_url": "/auth/perfil"
    }), 200)

    set_access_cookies(response, token)
    return response

# 📌 Obter Perfil do Usuário
def obter_perfil(usuario_id):
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return {"erro": "Usuário não encontrado."}, 404

    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "cpf": usuario.cpf,
        "telefone": usuario.telefone,
        "cidade": usuario.cidade,
        "estado": usuario.estado
    }, 200  # ✅ Agora retorna um dicionário válido


# 📌 Logout do Usuário
def logout_usuario():
    response = make_response(jsonify({"mensagem": "Logout realizado com sucesso."}))
    unset_jwt_cookies(response)
    return response, 200
