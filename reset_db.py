import psycopg2
from app.extensions import db
from app import create_app  # Certifique-se de importar a factory do seu Flask

# Configuração do Banco
DB_NAME = "sigseg"
DB_USER = "postgres"  # Altere se necessário
DB_PASSWORD = "241509"  # Coloque a senha correta
DB_HOST = "localhost"
DB_PORT = "5432"

def reset_database():
    """ Remove e recria o banco de dados """
    try:
        print("🚀 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        conn.autocommit = True  # Permite comandos como DROP DATABASE
        
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
            cur.execute(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};")
            print(f"✅ Banco de dados '{DB_NAME}' recriado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao recriar o banco: {e}")

    finally:
        if conn:
            conn.close()

def run_migrations():
    """ Aplica as migrações para recriar as tabelas """
    print("📌 Aplicando migrações...")
    app = create_app()  # Cria a aplicação Flask
    with app.app_context():
        db.create_all()  # Cria todas as tabelas

    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    reset_database()
    run_migrations()
    print("🎉 Banco de dados pronto para uso!")
