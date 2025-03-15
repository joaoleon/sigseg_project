from flask_login import UserMixin
from app.extensions import db, bcrypt

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)  # ✅ Nome correto da coluna

    telefone = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    genero = db.Column(db.String(20), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(50), nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)

    def set_senha(self, senha):
        if not senha or senha.strip() == "":
            raise ValueError("A senha não pode estar vazia.")

        self.senha = bcrypt.generate_password_hash(senha.strip()).decode("utf-8")

    def verificar_senha(self, senha):
        if not self.senha:
            print("❌ Erro: Senha armazenada é None ou inválida!")
            return False

        resultado = bcrypt.check_password_hash(self.senha, senha)
    
        print(f"📌 Senha digitada: {senha}")
        print(f"📌 Senha armazenada no banco: {self.senha}")
        print(f"✅ Senha correta? {resultado}")

        return resultado

    # 🔥 Métodos exigidos pelo Flask-Login 🔥
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):  # 🔥 Corrige o problema do Flask-Login não reconhecer `get_id()`
        return str(self.id)  # Retorna o ID como string
