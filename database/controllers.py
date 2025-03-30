# Importando as bibliotecas

from flask import Blueprint, request, jsonify
from custom_models import db, User, Order, TradeReport
from schemas import UserSchema, OrderSchema, TradeReportSchema

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