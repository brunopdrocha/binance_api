# Bibliotecas para criação de Banco de Dados / Teste

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Numeric, DateTime
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from datetime import datetime
import random

# Base Data
class Base(DeclarativeBase):
    pass

#Criação banco de Dados
db = SQLAlchemy(model_class=Base)

# Carrega as variáveis do .env
load_dotenv()

# User Data
class User(db.Model):
    __tablename__ = 'users'  # Adicionando nome explícito da tabela
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    binance_api_key: Mapped[str] = mapped_column(String(100), name='binanceApiKey', nullable=False)
    binance_secret_key: Mapped[str] = mapped_column(String(100), name='binanceSecretKey', nullable=False)
    saldo_inicio: Mapped[float] = mapped_column(Numeric(10, 2), name='saldoInicio', nullable=False)
    
    # Relacionamento bidirecional
    orders = relationship("Order", back_populates="user")

# Order Data
class Order(db.Model):
    __tablename__ = 'orders'  # Adicionando nome explícito da tabela
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)  
    side: Mapped[str] = mapped_column(String(20), nullable=False)  
    types: Mapped[str] = mapped_column(String(20), nullable=False)  
    quantity: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)  # 8 casas decimais para cripto
    price: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    timeInForce: Mapped[str] = mapped_column(String(20), nullable=False) 
    
    # Relacionamentos bidirecionais
    user = relationship("User", back_populates="orders")
    reports = relationship("TradeReport", back_populates="order")

# Trade Report Data
class TradeReport(db.Model):
    __tablename__ = 'trade_reports'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)
    profit_loss: Mapped[float] = mapped_column(Numeric(15, 2), nullable=True)
    report_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    
    # Relacionamento bidirecional
    order = relationship("Order", back_populates="reports")

# Função de Deste Dataable 
"""
if __name__ == "__main__":
    from flask import Flask
    
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
            
        except Exception as e:
            print("Erro:", str(e))
"""