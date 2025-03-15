from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from datetime import timedelta
from app.models.usuario import Usuario
from app.extensions import db, limiter

api_bp = Blueprint("api", __name__)

# 📌 Configuração do Rate Limit (Máx. 5 tentativas por minuto)
@api_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def api_login():
    print("🔍 Recebendo requisição de login...")

    try:
        data = request.get_json()
        print(f"📩 Dados recebidos: {data}")

        email = data.get("email", "").strip().lower()
        senha = data.get("password", "").strip() or data.get("senha", "").strip()

        if not email or not senha:
            return jsonify({"erro": "E-mail e senha são obrigatórios."}), 400

        user = Usuario.query.filter_by(email=email).first()
        if user and user.verificar_senha(senha):
            print(f"✅ Login bem-sucedido para: {email}")

            access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=3))  # 🔥 Verifique se `user.id` está correto
            print(f"🔑 Token gerado: {access_token}")

            return jsonify({
                "mensagem": "Login realizado com sucesso!",
                "access_token": access_token,
                "redirect_url": "/perfil"
            }), 200

    except Exception as e:
        print(f"❌ Erro no login: {e}")

    return jsonify({"erro": "Credenciais inválidas."}), 401


# 📌 Cadastro de Usuário (Registro)
@api_bp.route('/register', methods=['POST'])
def api_register():
    """ API para registrar um novo usuário via JSON. """
    print("🔍 Recebendo requisição de cadastro...")

    try:
        data = request.get_json()
        print(f"📩 Dados recebidos: {data}")

        nome = data.get("nome", "").strip()
        email = data.get("email", "").strip().lower()
        senha = data.get("senha", "").strip()
        cpf = data.get("cpf", "").strip()
        telefone = data.get("telefone", "").strip()
        cidade = data.get("cidade", "").strip()
        estado = data.get("estado", "").strip()

        if not nome or not email or not senha or not cpf:
            return jsonify({"erro": "Nome, e-mail, senha e CPF são obrigatórios."}), 400

        with current_app.app_context():
            if Usuario.query.filter_by(email=email).first():
                return jsonify({"erro": "E-mail já cadastrado."}), 409
            
            if Usuario.query.filter_by(cpf=cpf).first():
                return jsonify({"erro": "CPF já cadastrado."}), 409

            # Criar novo usuário
            novo_usuario = Usuario(
                nome=nome,
                email=email,
                cpf=cpf,
                telefone=telefone,
                cidade=cidade,
                estado=estado
            )
            novo_usuario.set_senha(senha)  # 🔹 Criptografar senha corretamente
            db.session.add(novo_usuario)
            db.session.commit()

            print(f"✅ Novo usuário cadastrado: {email}")

        return jsonify({"mensagem": "Cadastro realizado com sucesso!"}), 201

    except Exception as e:
        print(f"❌ Erro no cadastro: {e}")
        return jsonify({"erro": "Erro ao processar o cadastro."}), 500


# 📌 Verificação do status da API
@api_bp.route("/status", methods=["GET"])
def status():
    """ Retorna uma mensagem indicando que a API está funcionando corretamente. """
    return jsonify({"message": "API funcionando corretamente!"}), 200
