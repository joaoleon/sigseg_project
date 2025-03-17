import logging
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.services.main_service import obter_endereco, cadastrar_objeto
from app.services.monitoramento_service import obter_estatisticas_monitoramento
from app.models.objeto_roubado import ObjetoRoubado
from sqlalchemy.exc import SQLAlchemyError

# Configuração de logging para capturar erros no terminal
logging.basicConfig(level=logging.DEBUG)

main_bp = Blueprint("main", __name__)

# 📌 🔹 Página Inicial
@main_bp.route("/")
def home():
    return render_template("home.html")

# 📌 Rota da Página Monitoramento
@main_bp.route("/monitoramento")
@jwt_required()
def monitoramento():
    try:
        dados_monitoramento = obter_estatisticas_monitoramento()

        if isinstance(dados_monitoramento, tuple):  # 📌 Verifica se houve erro no retorno
            return render_template("monitoramento.html", stats={}, usuario_logado=True)

        return render_template(
            "monitoramento.html",
            stats=dados_monitoramento["stats"],
            ocorrencias_por_mes=dados_monitoramento["ocorrencias_por_mes"],
            ocorrencias_por_hora=dados_monitoramento["ocorrencias_por_hora"],
            tipo_mais_comum=dados_monitoramento["tipo_mais_comum"],
            localizacoes=dados_monitoramento["localizacoes"],
            usuario_logado=True
        )

    except Exception as e:
        logging.error(f"Erro inesperado ao carregar monitoramento: {str(e)}")
        return render_template("monitoramento.html", stats={}, usuario_logado=True)
    
# 📌 🔹 Página "Quem Somos"
@main_bp.route("/quem-somos")
def quem_somos():
    return render_template("quem_somos.html")

# 📌 🔹 Página de Contato
@main_bp.route("/contato")
def contato():
    return render_template("contato.html")

# 📌 🔹 Página "Meus Objetos"
@main_bp.route("/meus-objetos", methods=["GET"])
@jwt_required()
def meus_objetos():
    usuario_id = get_jwt_identity()
    pagina = request.args.get("pagina", 1, type=int)

    try:
        objetos_paginados = ObjetoRoubado.query.filter_by(usuario_id=usuario_id).paginate(
            page=pagina, per_page=10, error_out=False
        )
        return render_template(
            "meus_objetos.html",
            objetos=objetos_paginados.items if objetos_paginados else [],
            pagina_atual=objetos_paginados.page if objetos_paginados else 1,
            paginas_totais=objetos_paginados.pages if objetos_paginados else 1,
        )
    
    except SQLAlchemyError as e:
        logging.error(f"Erro ao carregar objetos do usuário: {str(e)}")
        flash("Erro ao carregar seus objetos cadastrados.", "danger")
        return render_template("meus_objetos.html", objetos=[])

# 📌 🔹 Obter Endereço pelo Geopy
@main_bp.route("/get_address")
def get_address():
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    try:
        response, status = obter_endereco(latitude, longitude)
        return jsonify(response), status
    except Exception as e:
        logging.error(f"Erro ao obter endereço: {str(e)}")
        return jsonify({"erro": "Não foi possível obter o endereço."}), 500

# 📌 🔹 Cadastrar Objeto
@main_bp.route("/cadastrar_objeto", methods=["GET", "POST"])
@jwt_required()
def cadastrar_objeto_view():
    if request.method == "GET":
        return render_template("cadastrar_objeto.html", usuario_logado=True)

    user_id = get_jwt_identity()
    
    try:
        # Captura os dados do formulário
        data = request.form.to_dict()

        # Conversão segura de latitude e longitude
        try:
            data["latitude"] = float(data["latitude"])
            data["longitude"] = float(data["longitude"])
        except (TypeError, ValueError):
            flash("Erro: Latitude e Longitude devem ser números válidos!", "danger")
            return redirect(url_for("main.cadastrar_objeto_view"))

        data["usuario_id"] = user_id  # Adiciona o ID do usuário ao objeto

        logging.debug(f"Enviando os seguintes dados para o serviço de cadastro: {data}")
        response, status = cadastrar_objeto(user_id, data)
        logging.debug(f"Resposta do serviço: {response}, Status: {status}")

        if status == 201:
            flash("Objeto registrado com sucesso!", "success")
            return redirect(url_for("main.cadastro_sucesso"))

        flash(f"Erro ao registrar o objeto: {response.get('erro', 'Erro desconhecido')}", "danger")
    
    except Exception as e:
        logging.error(f"Erro inesperado ao registrar objeto: {str(e)}")
        flash(f"Erro inesperado: {str(e)}", "danger")
    
    return redirect(url_for("main.cadastrar_objeto_view"))

# 📌 🔹 Página de Login
@main_bp.route("/login")
def login_view():
    return render_template("login.html")

# 📌 🔹 Página de Registro
@main_bp.route("/register")
def register():
    return render_template("register.html")

# 📌 🔹 Página de Confirmação de Cadastro Bem-Sucedido
@main_bp.route("/cadastro_sucesso")
def cadastro_sucesso():
    return render_template("cadastro_sucesso.html")

# 📌 🔹 Página de FAQ
@main_bp.route("/faq")
def faq():
    return render_template("faq.html", usuario_logado=False)

# 📌 🔹 Visualizar um Objeto Específico
@main_bp.route("/ver-objeto/<int:objeto_id>")
def ver_objeto(objeto_id):
    objeto = ObjetoRoubado.query.get_or_404(objeto_id)
    return render_template("ver_objeto.html", objeto=objeto)

# 📌 🔹 Injetar Status do Usuário Globalmente nos Templates
@main_bp.app_context_processor
def inject_user_status():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        return {"usuario_logado": bool(user_id)}
    except Exception:
        return {"usuario_logado": False}
