# Bibliotecas para criação de Banco de Dados / Teste

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Numeric, DateTime
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from datetime import datetime
import random

# Carrega as variáveis do .env
load_dotenv()

# Base Data
class Base(DeclarativeBase):
    pass

#Criação banco de Dados
db = SQLAlchemy(model_class=Base)

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
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)  # Ex: BTCUSDT
    quantity: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)  # 8 casas decimais para cripto
    buy_price: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    sell_price: Mapped[float] = mapped_column(Numeric(18, 8), nullable=True)  # Preenchido ao fechar a ordem
    stop_loss: Mapped[float] = mapped_column(Numeric(18, 8), nullable=True)
    take_profit: Mapped[float] = mapped_column(Numeric(18, 8), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='open')  # open, closed, canceled
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Tornando o campo nullable
    
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


# Função para teste de implementação para Banco de Dados mysql

#if __name__ == "__main__":
#    from flask import Flask
#    
#    app = Flask(__name__)
#
#    # Corrigindo a obtenção da variável de ambiente
#    database_url = os.getenv("DATABASE_URL")
#
#    if not database_url:
#        print("Erro: A variável DATABASE_URL não foi encontrada no ambiente.")
#    else:
#        print(f"Conectando ao banco de dados: {database_url}")
#
#    # Configuração para MySQL
#    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
#
#    db.init_app(app)
#    
#    with app.app_context():
#        try:
#            db.create_all()
#            print("Tabelas criadas com sucesso!")
#
#            # Definindo valores possíveis para as variáveis
#            symbols = ["BTCUSD", "ETHUSD", "BNBUSD", "ADAUSD", "SOLUSD"]
#
#            # Gerando valores aleatórios
#            # Usando uma instância da classe User em vez de um dicionário
#            new_user = User(
#                login=f"test_user{random.randint(10000, 99999)}",
#                password=f"test_{random.randint(10000, 99999)}_pass",
#                binance_api_key=f"api_key{random.randint(1000, 9999)}",
#                binance_secret_key=f"sec_key{random.randint(1000, 9999)}",
#                saldo_inicio=round(random.uniform(500.0, 5000.0), 2)
#            )
#
#            db.session.add(new_user)
#            db.session.commit()
#            print("Usuário inserido com sucesso!")
#            
#            # Agora que temos o ID do usuário, podemos criar uma ordem associada a ele
#            new_order = Order(
#                user_id=new_user.id,  # Usar o ID do usuário recém-criado
#                symbol=random.choice(symbols),
#                quantity=round(random.uniform(0.01, 2.0), 8),
#                buy_price=round(random.uniform(20000, 70000), 8),
#                sell_price=None,  # Ainda não fechada
#                stop_loss=round(random.uniform(15000, 25000), 8),
#                take_profit=round(random.uniform(75000, 90000), 8),
#                status="open",
#                created_at=datetime.utcnow(),
#                closed_at=None
#            )
#            
#            db.session.add(new_order)
#            db.session.commit()
#            print("Ordem inserida com sucesso!")
#            
#        except Exception as e:
#            print("Erro:", str(e))