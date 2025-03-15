from app.extensions import db
from datetime import datetime

class ObjetoRoubado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo_objeto = db.Column(db.String(50), nullable=False)
    transportadora = db.Column(db.String(100), nullable=True)  # ✅ Corrigido (certifique-se que está correto no backend)
    numero_serie = db.Column(db.String(50), nullable=True)
    forma_subtracao = db.Column(db.String(100), nullable=True)  # Ex: Furto, Assalto, Arrombamento
    meio_utilizado = db.Column(db.String(50), nullable=True)  # Ex: A pé, Moto, Carro, Bicicleta
    boletim_ocorrencia = db.Column(db.String(50), nullable=True)
    
    rua = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    cep = db.Column(db.String(20), nullable=True)  # Se disponível
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    data_ocorrencia = db.Column(db.Date, nullable=False)  # ✅ Mudado de `DateTime` para `Date`
    hora_ocorrencia = db.Column(db.Time, nullable=False)  # ✅ Mantido como `Time`
    
    foto = db.Column(db.String(255), nullable=True)  # Caminho da imagem salva (ex.: "uploads/fotos_objetos/abc123.jpg")
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

 # 🔥 Adicionando a data de cadastro corretamente
    data_cadastro = db.Column(db.DateTime, default=datetime.now)

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
            "rua": self.rua,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado,
            "cep": self.cep,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "data_ocorrencia": self.data_ocorrencia.strftime("%Y-%m-%d") if self.data_ocorrencia else None,
            "hora_ocorrencia": self.hora_ocorrencia.strftime("%H:%M") if self.hora_ocorrencia else None,
            "foto": self.foto if self.foto else "static/images/default.png",
            "usuario_id": self.usuario_id,
            "data_cadastro": self.data_cadastro.strftime("%Y-%m-%d") if self.data_cadastro else None
        }
