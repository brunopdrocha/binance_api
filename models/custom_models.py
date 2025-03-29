from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    binance_api_key: Mapped[str] = mapped_column(db.String(100), name='binanceApiKey', nullable=False)
    binance_secret_key: Mapped[str] = mapped_column(db.String(100), name='binanceSecretKey', nullable=False)
    saldo_inicio: Mapped[float] = mapped_column(db.Numeric(10, 2), name='saldoInicio', nullable=False)

if __name__ == "__main__":
    from flask import Flask
    import sqlalchemy as sa
    
    app = Flask(__name__)

    # Corrigindo a obtenção da variável de ambiente
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("Erro: A variável DATABASE_URL não foi encontrada no ambiente.")
    else:
        print(f"Conectando ao banco de dados: {database_url}")

    # Configuração para MySQL
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            print("Tabelas criadas com sucesso!")

            # Teste de inserção
            user = User(
                login="test_use52r44",
                password="test_5pa344ss",
                binance_api_key="t24est4_key",
                binance_secret_key="te3st4_sec1ret",
                saldo_inicio=1000.50
            )
            db.session.add(user)
            db.session.commit()
            print("Usuário inserido com sucesso!")
            
        except Exception as e:
            print("Erro:", str(e))
