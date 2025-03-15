from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.objetos_service import (
    adicionar_objeto, listar_objetos, atualizar_objeto, excluir_objeto, get_upload_folder
)

objetos_bp = Blueprint("objetos", __name__)

@objetos_bp.route("/uploads/<filename>")
def get_image(filename):
    return send_from_directory(get_upload_folder(), filename)

@objetos_bp.route("/objetos", methods=["POST"])
@jwt_required()
def adicionar_objeto_route():
    usuario_id = get_jwt_identity()
    data = request.form
    foto = request.files.get("foto")

    response, status = adicionar_objeto(data, foto, usuario_id)
    return jsonify(response), status

@objetos_bp.route("/objetos", methods=["GET"])
@jwt_required()
def listar_objetos_route():
    usuario_id = get_jwt_identity()
    filtros = request.args.to_dict()

    response, status = listar_objetos(usuario_id, filtros)
    return jsonify(response), status

@objetos_bp.route("/objetos/<int:objeto_id>", methods=["PUT"])
@jwt_required()
def atualizar_objeto_route(objeto_id):
    usuario_id = get_jwt_identity()
    data = request.form
    foto = request.files.get("foto")

    response, status = atualizar_objeto(objeto_id, data, foto, usuario_id)
    return jsonify(response), status

@objetos_bp.route("/objetos/<int:objeto_id>", methods=["DELETE"])
@jwt_required()
def excluir_objeto_route(objeto_id):
    usuario_id = get_jwt_identity()

    response, status = excluir_objeto(objeto_id, usuario_id)
    return jsonify(response), status
