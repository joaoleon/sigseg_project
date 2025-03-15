import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.objeto_roubado import ObjetoRoubado

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE_MB = 5  # Limite de 5MB

# 📌 Função para obter a pasta de uploads
def get_upload_folder():
    upload_folder = current_app.config.get("UPLOAD_FOLDER", os.path.join(current_app.root_path, 'app/static/uploads'))
    os.makedirs(upload_folder)  # 🔹 Garante que a pasta exista

    print(f"📌 UPLOAD_FOLDER definido como: {upload_folder}")  # 🔹 Depuração para ver onde está salvando
    return upload_folder

# 📌 Verifica se o arquivo tem uma extensão permitida
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# 📌 Salva a imagem e retorna o nome do arquivo salvo corretamente
def salvar_imagem(imagem):
    if imagem and allowed_file(imagem.filename):
        try:
            ext = imagem.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filename = secure_filename(filename)
            caminho_arquivo = os.path.join(get_upload_folder(), filename)

            print(f"📌 Salvando imagem em: {caminho_arquivo}")  # 🔹 Debug para ver onde a imagem será salva

            imagem.save(caminho_arquivo)
            return filename  # ✅ Agora só retorna o nome do arquivo, sem "static/uploads/"
        except Exception as e:
            print(f"❌ Erro ao salvar imagem: {str(e)}")
            return None
    return None

# 📌 Adiciona um novo objeto roubado ao banco de dados
def adicionar_objeto(data, foto, usuario_id):
    try:
        campos_obrigatorios = ["nome", "tipo_objeto", "endereco", "bairro", "cidade", "estado", "latitude", "longitude"]
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return {"erro": f"O campo '{campo}' é obrigatório."}, 400

        try:
            latitude = float(data["latitude"])
            longitude = float(data["longitude"])
        except ValueError:
            return {"erro": "Latitude e Longitude devem ser numéricos."}, 400

        if data["tipo_objeto"] in ["Celular", "Carro", "Moto"] and not data.get("numero_serie"):
            return {"erro": "Número de série é obrigatório para Celular, Carro e Moto."}, 400

        filename = salvar_imagem(foto) if foto else None

        novo_objeto = ObjetoRoubado(
            nome=data["nome"],
            tipo_objeto=data["tipo_objeto"],
            transportadora=data.get("transportadora"),
            numero_serie=data.get("numero_serie"),
            forma_subtracao=data.get("forma_subtracao"),
            descricao_suspeito=data.get("descricao_suspeito"),
            boletim_ocorrencia=data.get("boletim_ocorrencia"),
            endereco=data["endereco"],
            bairro=data["bairro"],
            cidade=data["cidade"],
            estado=data["estado"],
            latitude=latitude,
            longitude=longitude,
            foto=filename,
            usuario_id=usuario_id
        )

        db.session.add(novo_objeto)
        db.session.commit()
        return {"mensagem": "Objeto cadastrado com sucesso!", "objeto": novo_objeto.to_dict()}, 201

    except Exception as e:
        db.session.rollback()
        return {"erro": "Erro ao cadastrar objeto", "detalhe": str(e)}, 500

def listar_objetos(usuario_id, filtros, pagina=1, por_pagina=10):
    try:
        query = ObjetoRoubado.query.filter_by(usuario_id=usuario_id)

        if "tipo_objeto" in filtros:
            query = query.filter(ObjetoRoubado.tipo_objeto.ilike(f"%{filtros['tipo_objeto']}%"))
        if "endereco" in filtros:
            query = query.filter(ObjetoRoubado.endereco.ilike(f"%{filtros['endereco']}%"))

        objetos = query.paginate(page=pagina, per_page=por_pagina, error_out=False)
        return {
            "quantidade": objetos.total,
            "objetos": [obj.to_dict() for obj in objetos.items],
            "pagina_atual": objetos.page,
            "paginas_totais": objetos.pages,
        }, 200
    except Exception as e:
        return {"erro": "Erro ao buscar objetos", "detalhe": str(e)}, 500


# 📌 Atualiza um objeto roubado
def atualizar_objeto(objeto_id, data, foto, usuario_id):
    try:
        objeto = ObjetoRoubado.query.filter_by(id=objeto_id, usuario_id=usuario_id).first()

        if not objeto:
            return {"erro": "Objeto não encontrado."}, 404

        if objeto.usuario_id != usuario_id:
            return {"erro": "Você não tem permissão para modificar este objeto."}, 403

        if data.get("nome"):
            objeto.nome = data["nome"]
        if data.get("descricao"):
            objeto.descricao = data["descricao"]

        nova_foto = salvar_imagem(foto) if foto else None
        if nova_foto:
            if objeto.foto:
                caminho_antigo = os.path.join(get_upload_folder(), objeto.foto)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)

            objeto.foto = nova_foto

        db.session.commit()
        return {"mensagem": "Objeto atualizado com sucesso!", "objeto": objeto.to_dict()}, 200

    except Exception as e:
        db.session.rollback()
        return {"erro": "Erro ao atualizar objeto", "detalhe": str(e)}, 500

# 📌 Exclui um objeto roubado
def excluir_objeto(objeto_id, usuario_id):
    try:
        objeto = ObjetoRoubado.query.filter_by(id=objeto_id, usuario_id=usuario_id).first()

        if not objeto:
            return {"erro": "Objeto não encontrado."}, 404

        if objeto.usuario_id != usuario_id:
            return {"erro": "Você não tem permissão para excluir este objeto."}, 403

        if objeto.foto:
            caminho_imagem = os.path.join(get_upload_folder(), objeto.foto)
            if os.path.exists(caminho_imagem):
                os.remove(caminho_imagem)

        db.session.delete(objeto)
        db.session.commit()

        return {"mensagem": "Objeto excluído com sucesso!"}, 200

    except Exception as e:
        db.session.rollback()
        return {"erro": "Erro ao excluir objeto", "detalhe": str(e)}, 500

#Lista objetos dos usuários
def listar_objetos_para_template(usuario_id, pagina=1, por_pagina=10):
    """Retorna os objetos cadastrados pelo usuário para exibição em um template HTML."""
    try:
        objetos_paginados = ObjetoRoubado.query.filter_by(usuario_id=usuario_id).paginate(
            page=pagina, per_page=por_pagina, error_out=False
        )
        return objetos_paginados  # Retorna um objeto de paginação
    except Exception as e:
        print(f"❌ Erro ao buscar objetos: {e}")
        return None
