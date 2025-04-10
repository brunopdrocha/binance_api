# routes/api.py

from flask import Blueprint, request, jsonify
from database.custom_models import db, User, Order, TradeReport
from database.schemas import UserSchema, OrderSchema, TradeReportSchema
import requests
from binance.client import Client
from http import HTTPStatus

# Criação do Blueprint
bp = Blueprint('api', __name__)

# Instâncias dos Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
report_schema = TradeReportSchema()
reports_schema = TradeReportSchema(many=True)

# --- Rotas de Usuário ---

@bp.route('/users', methods=['POST'])
def create_user():
    """Criar um novo usuário"""
    try:
        user = User(**request.json)
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user), HTTPStatus.CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@bp.route('/users', methods=['GET'])
def get_users():
    """Obter todos os usuários"""
    users = User.query.all()
    return users_schema.jsonify(users), HTTPStatus.OK

@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obter um usuário específico pelo ID"""
    user = User.query.get_or_404(user_id)
    return user_schema.jsonify(user), HTTPStatus.OK

@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletar um usuário pelo ID"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuário deletado com sucesso"}), HTTPStatus.OK

# --- Rotas de Ordens ---

@bp.route('/users/<int:user_id>/orders', methods=['POST'])
def create_order(user_id):
    """Criar uma nova ordem para um usuário específico"""
    # Busca o usuário com base no ID
    user = User.query.get_or_404(user_id)

    try:
        # Instancia o cliente Binance com as chaves do usuário
        api_key = user.binance_api_key
        api_secret = user.binance_secret_key
        client = Client(api_key, api_secret, testnet=True)

        # Extrai os dados da ordem do corpo da requisição
        data = request.json
        data['user_id'] = user_id
        
        # Parâmetros da ordem
        symbol = data.get('symbol')
        side = data.get('side', 'BUY')
        order_type = data.get('type', 'LIMIT')
        quantity = data.get('quantity')
        price = data.get('price')
        time_in_force = data.get('timeInForce', 'GTC')

        # Envia a ordem para a Binance
        binance_order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            price=price,
            timeInForce=time_in_force
        )

        # Cria a instância da ordem no banco de dados
        order = Order(**data)
        db.session.add(order)
        db.session.commit()

        return jsonify({
            "message": "Ordem criada com sucesso",
            "order": order_schema.dump(order),
            "binance_response": binance_order
        }), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@bp.route('/orders', methods=['GET'])
def get_all_orders():
    """Obter todas as ordens"""
    orders = Order.query.all()
    return orders_schema.jsonify(orders), HTTPStatus.OK

@bp.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """Obter todas as ordens de um usuário específico"""
    # Verifica se o usuário existe
    User.query.get_or_404(user_id)
    
    orders = Order.query.filter_by(user_id=user_id).all()
    return orders_schema.jsonify(orders), HTTPStatus.OK

@bp.route('/users/<int:user_id>/orders/<int:order_id>', methods=['PUT'])
def update_order(user_id, order_id):
    """Atualizar uma ordem específica de um usuário"""
    # Busca a ordem que pertença ao user_id
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

    try:
        # Atualiza os campos enviados no JSON
        data = request.json
        for key, value in data.items():
            if hasattr(order, key):
                setattr(order, key, value)

        db.session.commit()
        return order_schema.jsonify(order), HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@bp.route('/users/<int:user_id>/orders/<int:order_id>', methods=['DELETE'])
def delete_order(user_id, order_id):
    """Deletar uma ordem específica de um usuário"""
    # Busca a ordem que pertença ao user_id
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

    try:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Ordem deletada com sucesso"}), HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

# --- Rotas de Relatórios de Trades ---

@bp.route('/reports', methods=['POST'])
def create_report():
    """Criar um novo relatório de trade"""
    try:
        report = TradeReport(**request.json)
        db.session.add(report)
        db.session.commit()
        return report_schema.jsonify(report), HTTPStatus.CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@bp.route('/users/<int:user_id>/reports', methods=['GET'])
def get_user_reports(user_id):
    """Obter todos os relatórios de trade de um usuário específico"""
    # Verifica se o usuário existe
    User.query.get_or_404(user_id)
    
    # Assumindo que TradeReport tem uma relação com Order que tem user_id
    reports = TradeReport.query.join(Order).filter(Order.user_id == user_id).all()
    return reports_schema.jsonify(reports), HTTPStatus.OK

@bp.route('/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """Atualizar um relatório de trade específico"""
    report = TradeReport.query.get_or_404(report_id)

    try:
        data = request.json
        for key, value in data.items():
            if hasattr(report, key):
                setattr(report, key, value)

        db.session.commit()
        return report_schema.jsonify(report), HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

@bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Deletar um relatório de trade específico"""
    report = TradeReport.query.get_or_404(report_id)

    try:
        db.session.delete(report)
        db.session.commit()
        return jsonify({"message": "Relatório deletado com sucesso"}), HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

# --- Rotas de Utilidades ---

@bp.route('/market/price/<string:symbol>', methods=['GET'])
def get_price(symbol):
    """Obter o preço atual de um símbolo na Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({"error": "Símbolo inválido ou erro na API"}), HTTPStatus.BAD_REQUEST

        data = response.json()
        return jsonify({
            "symbol": data["symbol"],
            "price": float(data["price"])
        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR