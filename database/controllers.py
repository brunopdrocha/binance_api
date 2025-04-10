# Importando as bibliotecas

from flask import Blueprint, request, jsonify
from database.custom_models import db, User, Order, TradeReport
from database.schemas import UserSchema, OrderSchema, TradeReportSchema
import requests
from binance.client import Client

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

### User ###

# Rota para criar user
@bp.route('/user', methods=['POST'])
def create_user():
    user = User(**request.json)
    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user)

@bp.route('/user', methods=['GET'])
def get_users():
    return users_schema.jsonify(User.query.all())

@bp.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return user_schema.jsonify(user)

@bp.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuário deletado"})

### Ordem ###

# Rota para as ordens de compra e venda
@bp.route('/orders/user/<int:id>', methods=['POST'])

def create_order(id):
    # Busca o usuário com base no ID
    user = User.query.get_or_404(id)

    # Instancia o cliente Binance com as chaves do usuário
    api_key = user.binance_api_key
    api_secret = user.binance_secret_key
    client = Client(api_key, api_secret, testnet=True)


    # Extrai os dados da ordem do corpo da requisição
    data = request.json

    # Pega os campos necessários
    data['user_id'] = id
    symbol = data.get('symbol')
    side = data.get('side', 'BUY')  # Padrão: BUY
    order_type = data.get('type', 'LIMIT')
    quantity = data.get('quantity')
    price = data.get('price')
    time_in_force = data.get('timeInForce', 'GTC')  # Padrão: GTC

    # Envia a ordem para a Binance
    try:
        binance_order = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            price=price,
            timeInForce=time_in_force
        )
        print("Ordem enviada com sucesso para Binance")

        # Cria a instância da ordem para o banco
        order = Order(**data)
        db.session.add(order)
        db.session.commit()

        return jsonify({
            "mensagem": "Ordem criada com sucesso",
            "binance_response": binance_order
        }), 201

    except Exception as e:
        print("Erro ao enviar ordem:", str(e))
        return jsonify({"erro": str(e)}), 400

@bp.route('/orders/user', methods=['GET'])
def get_orders():
    return orders_schema.jsonify(Order.query.all())

@bp.route('/orders/user/<int:id>', methods=['GET'])
def get_user_orders(id):
    user = User.query.get_or_404(id)
    orders = Order.query.filter_by(user_id=user.id).all()
    return orders_schema.jsonify(orders)

@bp.route('/orders/user/<int:user_id>/order/<int:order_id>', methods=['PUT'])
def update_user_order(user_id, order_id):
    # Busca a ordem que pertença ao user_id
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

    # Atualiza os campos enviados no JSON
    data = request.json
    for key in data:
        if hasattr(order, key):
            setattr(order, key, data[key])

    db.session.commit()
    return order_schema.jsonify(order)

@bp.route('/orders/user/<int:user_id>/order/<int:order_id>', methods=['DELETE'])
def delete_user_order(user_id, order_id):
    # Busca a ordem que pertença ao user_id
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Ordem deletada"})

### Trades ###

# Rotas para o report dos Trades
@bp.route('/reports', methods=['POST'])
def create_report():
    report = TradeReport(**request.json)
    db.session.add(report)
    db.session.commit()
    return report_schema.jsonify(report)

@bp.route('/reports/<int:id>', methods=['GET'])
def get_reports(id):
    return reports_schema.jsonify(TradeReport.query.all())

@bp.route('/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    report = TradeReport.query.get_or_404(report_id)
    data = request.json

    if 'order_id' in data:
        report.order_id = data['order_id']
    if 'profit_loss' in data:
        report.profit_loss = data['profit_loss']
    if 'report_date' in data:
        report.report_date = data['report_date']  # caso você queira aceitar uma data manualmente

    db.session.commit()
    return report_schema.jsonify(report)

@bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    report = TradeReport.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return jsonify({"message": "Relatório deletado com sucesso"})


@bp.route('/price/<string:symbol>', methods=['GET'])
def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Símbolo inválido ou erro na API"}), 400

    data = response.json()
    return jsonify({
        "symbol": data["symbol"],
        "price": float(data["price"])
    })