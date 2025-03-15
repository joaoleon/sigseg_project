from flask import Blueprint, request, jsonify
from app.services.usuarios_service import listar_usuarios, criar_usuario

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route("/usuarios", methods=["GET"])
def listar_usuarios_route():
    response, status = listar_usuarios()
    return jsonify(response), status

@usuarios_bp.route("/usuarios", methods=["POST"])
def criar_usuario_route():
    data = request.get_json()
    response, status = criar_usuario(data)
    return jsonify(response), status
