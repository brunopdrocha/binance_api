# Importando as bibliotecas

from flask import Blueprint, request, jsonify
from database.custom_models import db, User, Order, TradeReport
from database.schemas import UserSchema, OrderSchema, TradeReportSchema
import requests

# Chamando Blueprint
bp = Blueprint('api', __name__)

# Instance pros Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
report_schema = TradeReportSchema()
reports_schema = TradeReportSchema(many=True)

# --- ROTAS ---

# Rota para criar user
@bp.route('/users', methods=['POST'])
def create_user():
    user = User(**request.json)
    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user)

@bp.route('/users', methods=['GET'])
def get_users():
    return users_schema.jsonify(User.query.all())

@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return user_schema.jsonify(user)

@bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuário deletado"})

# Rota para as ordens de compra e venda
@bp.route('/orders', methods=['POST'])
def create_order():
    order = Order(**request.json)
    db.session.add(order)
    db.session.commit()
    return order_schema.jsonify(order)

@bp.route('/orders', methods=['GET'])
def get_orders():
    return orders_schema.jsonify(Order.query.all())

@bp.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    order = Order.query.get_or_404(id)
    data = request.json
    for key in data:
        if hasattr(order, key):
            setattr(order, key, data[key])
    db.session.commit()
    return order_schema.jsonify(order)

@bp.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Ordem deletada"})

# Rotas para o report dos Trades
@bp.route('/reports', methods=['POST'])
def create_report():
    report = TradeReport(**request.json)
    db.session.add(report)
    db.session.commit()
    return report_schema.jsonify(report)

@bp.route('/reports', methods=['GET'])
def get_reports():
    return reports_schema.jsonify(TradeReport.query.all())

@bp.route('/price/<string:symbol>', methods=['GET'])
def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Símbolo inválido ou erro na API"}), 400

    data = response.json()
    return jsonify({
        "moeda": data["symbol"],
        "preco": float(data["price"])
    })