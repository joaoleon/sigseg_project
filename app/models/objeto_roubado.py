from app.extensions import db
from datetime import datetime
import uuid
import re

class ObjetoRoubado(db.Model):
    __tablename__ = "objeto_roubado"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo_objeto = db.Column(db.String(50), nullable=False)
    transportadora = db.Column(db.String(100), nullable=True)
    numero_serie = db.Column(db.String(50), nullable=True)
    forma_subtracao = db.Column(db.String(100), nullable=True)  # Ex: Furto, Assalto, Arrombamento
    meio_utilizado = db.Column(db.String(50), nullable=True)  # Ex: A pé, Moto, Carro, Bicicleta
    boletim_ocorrencia = db.Column(db.String(255), nullable=True)  # Melhorado para armazenar BOs longos

    status = db.Column(db.String(20), nullable=False, default="Em investigação")  # Status do objeto

    rua = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False)

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    data_ocorrencia = db.Column(db.DateTime, nullable=False)  # Mantido como DateTime para fusos horários
    hora_ocorrencia = db.Column(db.Time, nullable=False)  # ✅ Adicionar este campo corretamente!
    
    foto = db.Column(db.String(255), nullable=True, default="static/images/default.png")
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)  # Mantido UTC
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def validar_coordenadas(self):
        """Valida latitude e longitude"""
        if not (-90 <= self.latitude <= 90 and -180 <= self.longitude <= 180):
            raise ValueError("Coordenadas inválidas.")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo_objeto": self.tipo_objeto,
            "transportadora": self.transportadora,
            "numero_serie": self.numero_serie,
            "forma_subtracao": self.forma_subtracao,
            "meio_utilizado": self.meio_utilizado,
            "boletim_ocorrencia": self.boletim_ocorrencia,
            "status": self.status,
            "rua": self.rua,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "data_ocorrencia": self.data_ocorrencia.strftime("%Y-%m-%d %H:%M:%S") if self.data_ocorrencia else None,
            "foto": self.foto,
            "usuario_id": self.usuario_id,
            "data_cadastro": self.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if self.data_cadastro else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }
