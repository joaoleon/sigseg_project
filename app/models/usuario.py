from flask_login import UserMixin
from app.extensions import db, bcrypt
from datetime import datetime
import re
import uuid

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    
    telefone = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    genero = db.Column(db.String(20), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(50), nullable=True)
    
    cpf = db.Column(db.String(255), unique=True, nullable=False)  # Será armazenado criptografado

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_senha(self, senha):
        if not senha or senha.strip() == "":
            raise ValueError("A senha não pode estar vazia.")

        self.senha = bcrypt.generate_password_hash(senha.strip()).decode("utf-8")

    def verificar_senha(self, senha):
        return bcrypt.check_password_hash(self.senha, senha)

    def set_cpf(self, cpf):
        """Armazena o CPF de forma criptografada."""
        if not re.match(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", cpf):
            raise ValueError("CPF inválido. Use o formato 000.000.000-00")
        self.cpf = bcrypt.generate_password_hash(cpf).decode("utf-8")

    def verificar_cpf(self, cpf):
        """Verifica se o CPF fornecido corresponde ao armazenado."""
        return bcrypt.check_password_hash(self.cpf, cpf)

    def formatar_telefone(self):
        """Normaliza o telefone para um formato padrão (XX) XXXXX-XXXX."""
        if self.telefone:
            self.telefone = re.sub(r"\D", "", self.telefone)  # Remove caracteres não numéricos
            if len(self.telefone) == 11:
                self.telefone = f"({self.telefone[:2]}) {self.telefone[2:7]}-{self.telefone[7:]}"
            elif len(self.telefone) == 10:
                self.telefone = f"({self.telefone[:2]}) {self.telefone[2:6]}-{self.telefone[6:]}"
            else:
                raise ValueError("Número de telefone inválido!")

    def get_id(self):
        """O Flask-Login requer uma string como ID, então usamos UUID."""
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False
