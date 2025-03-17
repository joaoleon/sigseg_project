from flask import Blueprint, request, jsonify, render_template, make_response, Response, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from app.services.auth_service import registrar_usuario, login_usuario, obter_perfil, logout_usuario
from app.models.objeto_roubado import ObjetoRoubado
from app.models.usuario import Usuario
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

# 📌 🔹 Cadastro de Usuário (Registro)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form.to_dict() if request.form else request.get_json()  # Captura os dados do formulário ou JSON
        
        response, status = registrar_usuario(data)  # Chama o serviço
        
        if status == 201:
            flash(response["mensagem"], "success")
            return redirect(response["redirect_url"])
        else:
            flash(response["erro"], "danger")
            return render_template("register.html"), status  # Retorna a página com erro

    return render_template("register.html")  # Exibe o formulário no GET
# 📌 🔹 Login de Usuário
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", usuario_logado=False)

    data = request.get_json()  # Captura os dados da requisição
    response = login_usuario(data)  # Chama a função de login

    if isinstance(response, tuple):  # ✅ Se a função retornar uma tupla (dicionário, status)
        content, status = response
        return jsonify(content), status  # 🔥 Retorna JSON corretamente

    if isinstance(response, Response):  # ✅ Se a função já retornou um Response, retorna direto
        return response

    return jsonify({"erro": "Erro inesperado no login"}), 500  # ✅ Captura erros inesperados

# 📌 🔹 Perfil do Usuário
@auth_bp.route("/perfil", methods=["GET"])
@jwt_required(locations=["cookies"])  # 🔥 Verifica o login diretamente no backend
def perfil():
    user_id = get_jwt_identity()
    response, status = obter_perfil(user_id)

    if status == 200:
        total_objetos = ObjetoRoubado.query.filter_by(usuario_id=user_id).count()
        return render_template("perfil.html", usuario=response, usuario_logado=True)  # ✅ Passando `usuario_logado=True`
    
    return jsonify(response), status


# 📌 🔹 Logout do Usuário
@auth_bp.route('/logout', methods=['GET', 'POST'])
@jwt_required(locations=["cookies"])
def user_logout():
    response = redirect(url_for('main.home'))  # Redireciona para a homepage
    unset_jwt_cookies(response)  # Remove o token JWT
    flash("Logout realizado com sucesso.", "success")
    return response

@auth_bp.route('/editar_perfil', methods=['POST'])
@jwt_required(locations=["cookies"])
def editar_perfil():
    user_id = get_jwt_identity()
    usuario = Usuario.query.get(user_id)

    if not usuario:
        flash("Usuário não encontrado!", "danger")
        return redirect(url_for('auth.perfil'))

    usuario.nome = request.form.get("nome", usuario.nome)
    usuario.telefone = request.form.get("telefone", usuario.telefone)
    usuario.cidade = request.form.get("cidade", usuario.cidade)
    usuario.estado = request.form.get("estado", usuario.estado)

    db.session.commit()

    flash("Perfil atualizado com sucesso!", "success")
    return redirect(url_for('auth.perfil'))


@auth_bp.route("/upload_foto", methods=["POST"])
def upload_foto():
    """Faz upload da foto de perfil"""
    if "foto_perfil" not in request.files:
        flash("Nenhum arquivo foi selecionado.", "danger")
        return redirect(url_for("auth.perfil"))

    file = request.files["foto_perfil"]
    
    if file.filename == "":
        flash("Nenhum arquivo foi selecionado.", "danger")
        return redirect(url_for("auth.perfil"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Simulação de atualização do usuário (se estiver usando banco de dados, adicione o código aqui)
        flash("Foto de perfil atualizada com sucesso!", "success")
        return redirect(url_for("auth.perfil"))
    
    flash("Formato de arquivo não permitido!", "danger")
    return redirect(url_for("auth.perfil"))

# 📌 🔹 Status de Autenticação

@auth_bp.route("/status", methods=["GET"])
@jwt_required(locations=["cookies"])  # ✅ Agora verifica os cookies corretamente
def auth_status():
    user_id = get_jwt_identity()
    return jsonify({"logged_in": bool(user_id)})  # ✅ Retorna um JSON válido
