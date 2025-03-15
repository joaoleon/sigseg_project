import os
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import request
from app.extensions import db
from app.models.objeto_roubado import ObjetoRoubado
from app.models.usuario import Usuario

# 📌 Configuração do diretório para salvar imagens
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Garantir que a pasta de uploads existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def salvar_imagem():
    """Salva a imagem no servidor e retorna o caminho salvo no banco de dados."""
    if "foto" not in request.files:
        return None  # Nenhuma imagem enviada

    file = request.files["foto"]
    if file.filename == "":
        return None  # Nenhum arquivo selecionado

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Evita nomes duplicados
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # 🔹 Converter caminho para formato web-friendly (substituir "\" por "/")
        file_path = file_path.replace("\\", "/")  

        return file_path  # Agora o caminho da imagem está correto

    return None


# 📌 Função para obter endereço pelo Geopy
def obter_endereco(latitude, longitude, tentativas=2):
    if not latitude or not longitude:
        return {"erro": "Parâmetros latitude e longitude são obrigatórios"}, 400

    geolocator = Nominatim(user_agent="sigseg_app")  

    for tentativa in range(tentativas):
        try:
            location = geolocator.reverse((latitude, longitude), exactly_one=True, timeout=10)

            if location and location.raw.get("address"):
                address_data = location.raw["address"]
                return {
                    "endereco_completo": location.address,
                    "estado": address_data.get("state", "Não encontrado"),
                    "cidade": address_data.get("city", address_data.get("town", address_data.get("village", "Não encontrado"))),
                    "bairro": address_data.get("suburb", "Não encontrado"),
                    "rua": address_data.get("road", "Não encontrado"),
                    "cep": address_data.get("postcode", "Não encontrado")
                }, 200

            return {"erro": "Endereço não encontrado"}, 404

        except GeocoderTimedOut:
            if tentativa == tentativas - 1:  
                return {"erro": "O serviço de geolocalização demorou muito para responder"}, 500

        except Exception as e:
            return {"erro": "Erro ao obter endereço", "detalhe": str(e)}, 500


# 📌 Função para cadastrar um objeto roubado (Agora Salvando Imagens)
def cadastrar_objeto(usuario_id, data):
    campos_obrigatorios = ["nome", "tipo_objeto", "rua", "bairro", "cidade", "estado", "latitude", "longitude", "data_ocorrencia", "hora_ocorrencia"]
    if not all(campo in data and data[campo] for campo in campos_obrigatorios):
        return {"erro": "Todos os campos obrigatórios devem ser preenchidos"}, 400

    try:
        # Converter datas para o formato correto
        data_ocorrencia = datetime.strptime(data["data_ocorrencia"], "%Y-%m-%d").date()
        hora_ocorrencia = datetime.strptime(data["hora_ocorrencia"], "%H:%M").time()

        # Salvar a imagem e obter o caminho salvo
        caminho_imagem = salvar_imagem()

        campos_validos = {
            "usuario_id", "nome", "tipo_objeto", "numero_serie", "transportadora",
            "meio_utilizado", "forma_subtracao", "boletim_ocorrencia",
            "rua", "bairro", "cidade", "estado", "cep",
            "latitude", "longitude", "data_ocorrencia", "hora_ocorrencia", "foto"
        }

        # Filtrar somente os campos válidos
        data_filtrado = {key: value for key, value in data.items() if key in campos_validos}
        data_filtrado["usuario_id"] = usuario_id
        data_filtrado["foto"] = caminho_imagem  # Salva o caminho da imagem no banco

        novo_objeto = ObjetoRoubado(**data_filtrado)

        db.session.add(novo_objeto)
        db.session.commit()

        return {"mensagem": "Objeto registrado com sucesso!", "foto": caminho_imagem}, 201

    except ValueError as ve:
        db.session.rollback()
        return {"erro": "Erro ao processar data/hora da ocorrência", "detalhe": str(ve)}, 400

    except Exception as e:
        db.session.rollback()
        return {"erro": "Erro ao registrar objeto", "detalhe": str(e)}, 500

# 📌 Função para obter perfil do usuário
def obter_perfil(usuario_id):
    try:
        usuario = Usuario.query.get(usuario_id)

        if not usuario:
            return {"erro": "Usuário não encontrado"}, 404

        return {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "cpf": usuario.cpf,
            "telefone": usuario.telefone,
            "cidade": usuario.cidade,
            "estado": usuario.estado
        }, 200

    except Exception as e:
        return {"erro": "Erro ao carregar perfil", "detalhe": str(e)}, 500
