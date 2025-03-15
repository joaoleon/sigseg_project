import logging
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.main_service import obter_endereco, cadastrar_objeto, obter_perfil
from app.services.auth_service import registrar_usuario, login_usuario, obter_perfil, logout_usuario
from app.services.monitoramento_service import obter_estatisticas_monitoramento
from app.models.objeto_roubado import ObjetoRoubado
import pandas as pd
import json

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
    dados_monitoramento = obter_estatisticas_monitoramento()

    if "erro" in dados_monitoramento:
        return render_template("monitoramento.html", usuario_logado=True, objetos=[], stats={})

    return render_template(
        "monitoramento.html",
        stats=dados_monitoramento["stats"],
        ocorrencias_por_mes=dados_monitoramento["ocorrencias_por_mes"],
        ocorrencias_por_hora=dados_monitoramento["ocorrencias_por_hora"],
        localizacoes=dados_monitoramento["localizacoes"],
        usuario_logado=True
    )

# 📌 🔹 Página "Quem Somos"
@main_bp.route("/quem-somos")
def quem_somos():
    return render_template("quem_somos.html")

# 📌 🔹 Página de Contato
@main_bp.route("/contato")
def contato():
    return render_template("contato.html")

# 📌 🔹 Meus Objetos (Protegido)
@main_bp.route("/meus-objetos", methods=["GET"])
@jwt_required()
def meus_objetos():
    usuario_id = get_jwt_identity()
    pagina = request.args.get("pagina", 1, type=int)

    objetos_paginados = ObjetoRoubado.query.filter_by(usuario_id=usuario_id).paginate(
        page=pagina, per_page=10, error_out=False
    )

    return render_template(
        "meus_objetos.html",
        objetos=objetos_paginados.items if objetos_paginados else [],
        pagina_atual=objetos_paginados.page if objetos_paginados else 1,
        paginas_totais=objetos_paginados.pages if objetos_paginados else 1,
    )

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

@main_bp.route("/cadastrar_objeto", methods=["GET", "POST"])
@jwt_required()
def cadastrar_objeto_view():
    if request.method == "GET":
        return render_template("cadastrar_objeto.html", usuario_logado=True)

    user_id = get_jwt_identity()

    # Captura os dados do formulário
    data = {
        "nome": request.form.get("nome"),
        "tipo_objeto": request.form.get("tipo_objeto"),
        "transportadora": request.form.get("transportadora"),
        "numero_serie": request.form.get("numero_serie"),
        "meio_utilizado": request.form.get("meio_utilizado"),
        "forma_subtracao": request.form.get("forma_subtracao"),
        "boletim_ocorrencia": request.form.get("boletim_ocorrencia"),
        "rua": request.form.get("rua"),
        "bairro": request.form.get("bairro"),
        "cidade": request.form.get("cidade"),
        "estado": request.form.get("estado"),
        "cep": request.form.get("cep"),
        "latitude": request.form.get("latitude"),
        "longitude": request.form.get("longitude"),
        "data_ocorrencia": request.form.get("data_ocorrencia"),
        "hora_ocorrencia": request.form.get("hora_ocorrencia"),
    }

    # Validação dos campos obrigatórios
    campos_obrigatorios = ["nome", "tipo_objeto", "rua", "bairro", "cidade", "estado", "latitude", "longitude", "data_ocorrencia", "hora_ocorrencia"]
    
    campos_faltando = [campo for campo in campos_obrigatorios if not data.get(campo)]
    if campos_faltando:
        flash(f"Os seguintes campos são obrigatórios e estão vazios: {', '.join(campos_faltando)}", "danger")
        return redirect(url_for("main.cadastrar_objeto_view"))

    # Conversão segura de latitude e longitude
    try:
        data["latitude"] = float(data["latitude"])
        data["longitude"] = float(data["longitude"])
    except (TypeError, ValueError):
        flash("Erro: Latitude e Longitude devem ser números válidos!", "danger")
        return redirect(url_for("main.cadastrar_objeto_view"))

    # Remove campos inválidos antes de passar para o serviço
    campos_validos = {
        "nome", "tipo_objeto", "transportadora", "numero_serie", "meio_utilizado", 
        "forma_subtracao", "boletim_ocorrencia", "rua", "bairro", "cidade", "estado", 
        "cep", "latitude", "longitude", "data_ocorrencia", "hora_ocorrencia", "usuario_id"
    }
    data_filtrado = {key: value for key, value in data.items() if key in campos_validos}
    data_filtrado["usuario_id"] = user_id

    # Tentativa de cadastro do objeto
    try:
        logging.debug(f"Enviando os seguintes dados para o serviço de cadastro: {data_filtrado}")
        response, status = cadastrar_objeto(user_id, data_filtrado)
        logging.debug(f"Resposta do serviço: {response}, Status: {status}")

        if status == 201:
            flash("Objeto registrado com sucesso!", "success")
            return redirect(url_for("main.cadastro_sucesso"))

        flash(f"Erro ao registrar o objeto: {response.get('erro', 'Erro desconhecido')}", "danger")
        return redirect(url_for("main.cadastrar_objeto_view"))

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

@main_bp.route("/faq")
def faq():
    return render_template("faq.html", usuario_logado=False)

@main_bp.route("/ver-objeto/<int:objeto_id>")
def ver_objeto(objeto_id):
    objeto = ObjetoRoubado.query.get_or_404(objeto_id)
    return render_template("ver_objeto.html", objeto=objeto)

@main_bp.app_context_processor  # 🔥 Agora `usuario_logado` estará disponível em todos os templates
def inject_user_status():
    try:
        verify_jwt_in_request(optional=True)  # ✅ Verifica se há um JWT válido nos cookies
        user_id = get_jwt_identity()
        return {"usuario_logado": bool(user_id)}  # 🔥 Agora todas as páginas sabem se o usuário está logado
    except Exception:
        return {"usuario_logado": False}