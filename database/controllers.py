# ================================
# IMPORTAÇÕES DAS BIBLIOTECAS
# ================================
from flask import Blueprint, request, jsonify
from database.custom_models import db, User, Order, TradeReport
from database.schemas import UserSchema, OrderSchema, TradeReportSchema
import requests
from binance.client import Client
from http import HTTPStatus

# ================================
# CONFIGURAÇÃO DO BLUEPRINT
# ================================
# Criação do Blueprint para organizar as rotas da API
bp = Blueprint('api', __name__)

# ================================
# INSTÂNCIAS DOS SCHEMAS MARSHMALLOW
# ================================
# Schemas para serialização/deserialização dos dados
user_schema = UserSchema()          # Para um único usuário
users_schema = UserSchema(many=True)  # Para múltiplos usuários
order_schema = OrderSchema()        # Para uma única ordem
orders_schema = OrderSchema(many=True)  # Para múltiplas ordens
report_schema = TradeReportSchema()  # Para um único relatório
reports_schema = TradeReportSchema(many=True)  # Para múltiplos relatórios

# ================================
# ROTAS DE USUÁRIO - CRUD COMPLETO
# ================================

@bp.route('/teste',methods=['GET'])
def ola():

    try:
        return jsonify({"sucess":"Sua api esta funcionando"}),HTTPStatus.OK

    except Exception as e:
        return jsonify({"error": "Sua api esta funcionando"}), HTTPStatus.INTERNAL_SERVER_ERROR
    

@bp.route('/users', methods=['POST'])
def create_user():
    """
    Criar um novo usuário no sistema
    
    Método: POST
    Endpoint: /users
    
    Parâmetros esperados no JSON:
    - name (str): Nome do usuário
    - email (str): Email do usuário
    - binance_api_key (str): Chave da API da Binance
    - binance_secret_key (str): Chave secreta da API da Binance
    
    Retornos:
    - 201: Usuário criado com sucesso + dados do usuário
    - 400: Erro na criação (dados inválidos, email duplicado, etc.)
    
    Exemplo de uso:
    POST /users
    {
        "name": "João Silva",
        "email": "joao@email.com",
        "binance_api_key": "sua_api_key",
        "binance_secret_key": "sua_secret_key"
    }
    """
    try:
        # Extrai os dados do JSON da requisição e cria instância do usuário
        user_data = request.json
        user = User(**user_data)
        
        # Adiciona o usuário ao banco de dados
        db.session.add(user)
        db.session.commit()
        
        # Retorna os dados do usuário criado serializado
        return user_schema.jsonify(user), HTTPStatus.CREATED
        
    except Exception as e:
        # Em caso de erro, desfaz a transação e retorna erro
        db.session.rollback()
        return jsonify({"error": f"Erro ao criar usuário: {str(e)}"}), HTTPStatus.BAD_REQUEST


@bp.route('/users', methods=['GET'])
def get_users():
    """
    Obter todos os usuários cadastrados no sistema
    
    Método: GET
    Endpoint: /users
    
    Parâmetros: Nenhum
    
    Retornos:
    - 200: Lista de todos os usuários + seus dados
    
    Exemplo de uso:
    GET /users
    """
    try:
        # Busca todos os usuários no banco de dados
        users = User.query.all()
        
        # Serializa e retorna a lista de usuários
        return users_schema.jsonify(users), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar usuários: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Obter um usuário específico pelo seu ID
    
    Método: GET
    Endpoint: /users/{user_id}
    
    Parâmetros da URL:
    - user_id (int): ID único do usuário
    
    Retornos:
    - 200: Dados do usuário encontrado
    - 404: Usuário não encontrado
    
    Exemplo de uso:
    GET /users/1
    """
    try:
        # Busca o usuário pelo ID, retorna 404 se não encontrar
        user = User.query.get_or_404(user_id)
        
        # Serializa e retorna os dados do usuário
        return user_schema.jsonify(user), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar usuário: {str(e)}"}), HTTPStatus.NOT_FOUND


@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Deletar um usuário pelo seu ID
    
    Método: DELETE
    Endpoint: /users/{user_id}
    
    Parâmetros da URL:
    - user_id (int): ID único do usuário a ser deletado
    
    Retornos:
    - 200: Usuário deletado com sucesso
    - 404: Usuário não encontrado
    - 400: Erro ao deletar (relacionamentos existentes, etc.)
    
    Exemplo de uso:
    DELETE /users/1
    """
    try:
        # Busca o usuário pelo ID, retorna 404 se não encontrar
        user = User.query.get_or_404(user_id)
        
        # Remove o usuário do banco de dados
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "Usuário deletado com sucesso"}), HTTPStatus.OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao deletar usuário: {str(e)}"}), HTTPStatus.BAD_REQUEST

# ================================
# ROTAS DE ORDENS - INTEGRAÇÃO BINANCE
# ================================

@bp.route('/users/<int:user_id>/orders', methods=['POST'])
def create_order(user_id):
    """
    Criar uma nova ordem de trading para um usuário específico
    Integra diretamente com a API da Binance para executar a ordem
    
    Método: POST
    Endpoint: /users/{user_id}/orders
    
    Parâmetros da URL:
    - user_id (int): ID do usuário que está criando a ordem
    
    Parâmetros esperados no JSON:
    - symbol (str): Par de trading (ex: 'BTCUSDT')
    - side (str): 'BUY' ou 'SELL'
    - type (str): Tipo da ordem ('LIMIT', 'MARKET', etc.)
    - quantity (float): Quantidade a ser negociada
    - price (float): Preço da ordem (obrigatório para LIMIT)
    - timeInForce (str): 'GTC', 'IOC', 'FOK' (padrão: 'GTC')
    
    Retornos:
    - 201: Ordem criada com sucesso + resposta da Binance
    - 400: Erro na criação (saldo insuficiente, parâmetros inválidos, etc.)
    - 404: Usuário não encontrado
    
    Exemplo de uso:
    POST /users/1/orders
    {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": "0.001",
        "price": "45000.00",
        "timeInForce": "GTC"
    }
    """
    try:
        # Busca o usuário e suas credenciais da Binance
        user = User.query.get_or_404(user_id)
        
        # Extrai dados da requisição e adiciona o user_id
        order_data = request.json
        order_data['user_id'] = user_id
        
        # Configuração do cliente Binance com as credenciais do usuário
        api_key = user.binance_api_key
        api_secret = user.binance_secret_key
        
        # Inicializa cliente Binance (testnet=True para ambiente de teste)
        client = Client(api_key, api_secret, testnet=True)
        
        # Extrai parâmetros da ordem
        symbol = order_data.get('symbol')
        side = order_data.get('side', 'BUY')
        order_type = order_data.get('type', 'LIMIT')
        quantity = order_data.get('quantity')
        price = order_data.get('price')
        time_in_force = order_data.get('timeInForce', 'GTC')
        
        # Envia a ordem para a Binance API
        binance_response = client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            price=price,
            timeInForce=time_in_force
        )
        
        # Salva a ordem no banco de dados local
        order = Order(**order_data)
        db.session.add(order)
        db.session.commit()
        
        # Retorna confirmação com dados da ordem local e resposta da Binance
        return jsonify({
            "message": "Ordem criada com sucesso",
            "local_order": order_schema.dump(order),
            "binance_response": binance_response
        }), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao criar ordem: {str(e)}"}), HTTPStatus.BAD_REQUEST


@bp.route('/orders', methods=['GET'])
def get_all_orders():
    """
    Obter todas as ordens do sistema (todos os usuários)
    
    Método: GET
    Endpoint: /orders
    
    Parâmetros: Nenhum
    
    Retornos:
    - 200: Lista de todas as ordens do sistema
    
    Exemplo de uso:
    GET /orders
    """
    try:
        # Busca todas as ordens no banco de dados
        orders = Order.query.all()
        
        # Serializa e retorna todas as ordens
        return orders_schema.jsonify(orders), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar ordens: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@bp.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """
    Obter todas as ordens de um usuário específico
    
    Método: GET
    Endpoint: /users/{user_id}/orders
    
    Parâmetros da URL:
    - user_id (int): ID do usuário
    
    Retornos:
    - 200: Lista de ordens do usuário
    - 404: Usuário não encontrado
    
    Exemplo de uso:
    GET /users/1/orders
    """
    try:
        # Verifica se o usuário existe (retorna 404 se não existir)
        User.query.get_or_404(user_id)
        
        # Busca todas as ordens do usuário específico
        orders = Order.query.filter_by(user_id=user_id).all()
        
        # Serializa e retorna as ordens do usuário
        return orders_schema.jsonify(orders), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar ordens do usuário: {str(e)}"}), HTTPStatus.NOT_FOUND


@bp.route('/users/<int:user_id>/orders/<int:order_id>', methods=['PUT'])
def update_order(user_id, order_id):
    """
    Atualizar uma ordem específica de um usuário
    Permite modificar campos como status, observações, etc.
    
    Método: PUT
    Endpoint: /users/{user_id}/orders/{order_id}
    
    Parâmetros da URL:
    - user_id (int): ID do usuário proprietário da ordem
    - order_id (int): ID da ordem a ser atualizada
    
    Parâmetros esperados no JSON:
    - Qualquer campo válido do modelo Order que se deseja atualizar
    
    Retornos:
    - 200: Ordem atualizada com sucesso
    - 404: Usuário ou ordem não encontrada
    - 400: Erro na atualização
    
    Exemplo de uso:
    PUT /users/1/orders/5
    {
        "status": "FILLED",
        "notes": "Ordem executada com sucesso"
    }
    """
    try:
        # Busca a ordem específica que pertence ao usuário
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
        
        # Extrai dados da requisição
        update_data = request.json
        
        # Atualiza apenas os campos enviados na requisição
        for field, value in update_data.items():
            if hasattr(order, field):
                setattr(order, field, value)
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        # Retorna a ordem atualizada
        return order_schema.jsonify(order), HTTPStatus.OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao atualizar ordem: {str(e)}"}), HTTPStatus.BAD_REQUEST


@bp.route('/users/<int:user_id>/orders/<int:order_id>', methods=['DELETE'])
def delete_order(user_id, order_id):
    """
    Deletar uma ordem específica de um usuário
    
    Método: DELETE
    Endpoint: /users/{user_id}/orders/{order_id}
    
    Parâmetros da URL:
    - user_id (int): ID do usuário proprietário da ordem
    - order_id (int): ID da ordem a ser deletada
    
    Retornos:
    - 200: Ordem deletada com sucesso
    - 404: Usuário ou ordem não encontrada
    - 400: Erro ao deletar
    
    Exemplo de uso:
    DELETE /users/1/orders/5
    """
    try:
        # Busca a ordem específica que pertence ao usuário
        order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
        
        # Remove a ordem do banco de dados
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({"message": "Ordem deletada com sucesso"}), HTTPStatus.OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao deletar ordem: {str(e)}"}), HTTPStatus.BAD_REQUEST

# ================================
# ROTAS DE RELATÓRIOS DE TRADE
# ================================

@bp.route('/reports', methods=['POST'])
def create_report():
    """
    Criar um novo relatório de trade
    
    Método: POST
    Endpoint: /reports
    
    Parâmetros esperados no JSON:
    - order_id (int): ID da ordem relacionada ao relatório
    - profit_loss (float): Lucro ou prejuízo da operação
    - fees (float): Taxas cobradas na operação
    - notes (str): Observações sobre o trade
    
    Retornos:
    - 201: Relatório criado com sucesso
    - 400: Erro na criação
    
    Exemplo de uso:
    POST /reports
    {
        "order_id": 1,
        "profit_loss": 150.50,
        "fees": 2.75,
        "notes": "Trade bem-sucedido em BTC"
    }
    """
    try:
        # Extrai dados da requisição e cria instância do relatório
        report_data = request.json
        report = TradeReport(**report_data)
        
        # Adiciona o relatório ao banco de dados
        db.session.add(report)
        db.session.commit()
        
        # Retorna o relatório criado serializado
        return report_schema.jsonify(report), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao criar relatório: {str(e)}"}), HTTPStatus.BAD_REQUEST


@bp.route('/users/<int:user_id>/reports', methods=['GET'])
def get_user_reports(user_id):
    """
    Obter todos os relatórios de trade de um usuário específico
    
    Método: GET
    Endpoint: /users/{user_id}/reports
    
    Parâmetros da URL:
    - user_id (int): ID do usuário
    
    Retornos:
    - 200: Lista de relatórios do usuário
    - 404: Usuário não encontrado
    
    Exemplo de uso:
    GET /users/1/reports
    """
    try:
        # Verifica se o usuário existe
        User.query.get_or_404(user_id)
        
        # Busca relatórios através da relação com Order
        # JOIN: TradeReport -> Order -> User
        reports = TradeReport.query.join(Order).filter(Order.user_id == user_id).all()
        
        # Serializa e retorna os relatórios
        return reports_schema.jsonify(reports), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar relatórios: {str(e)}"}), HTTPStatus.NOT_FOUND

#Relatorio de trade

@bp.route('/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """
    Atualizar um relatório de trade específico
    
    Método: PUT
    Endpoint: /reports/{report_id}
    
    Parâmetros da URL:
    - report_id (int): ID do relatório a ser atualizado
    
    Parâmetros esperados no JSON:
    - Qualquer campo válido do modelo TradeReport
    
    Retornos:
    - 200: Relatório atualizado com sucesso
    - 404: Relatório não encontrado
    - 400: Erro na atualização
    
    Exemplo de uso:
    PUT /reports/1
    {
        "profit_loss": 200.75,
        "notes": "Análise atualizada do trade"
    }
    """
    try:
        # Busca o relatório pelo ID
        report = TradeReport.query.get_or_404(report_id)
        
        # Extrai dados da requisição
        update_data = request.json
        
        # Atualiza apenas os campos enviados
        for field, value in update_data.items():
            if hasattr(report, field):
                setattr(report, field, value)
        
        # Salva as alterações
        db.session.commit()
        
        # Retorna o relatório atualizado
        return report_schema.jsonify(report), HTTPStatus.OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao atualizar relatório: {str(e)}"}), HTTPStatus.BAD_REQUEST


@bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """
    Deletar um relatório de trade específico
    
    Método: DELETE
    Endpoint: /reports/{report_id}
    
    Parâmetros da URL:
    - report_id (int): ID do relatório a ser deletado
    
    Retornos:
    - 200: Relatório deletado com sucesso
    - 404: Relatório não encontrado
    - 400: Erro ao deletar
    
    Exemplo de uso:
    DELETE /reports/1
    """
    try:
        # Busca o relatório pelo ID
        report = TradeReport.query.get_or_404(report_id)
        
        # Remove o relatório do banco de dados
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({"message": "Relatório deletado com sucesso"}), HTTPStatus.OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao deletar relatório: {str(e)}"}), HTTPStatus.BAD_REQUEST

# ================================
# ROTAS DE UTILIDADES - DADOS DE MERCADO
# ================================

@bp.route('/market/price/<string:symbol>', methods=['GET'])
def get_price(symbol):
    """
    Obter o preço atual de um símbolo/par de trading na Binance
    Consulta diretamente a API pública da Binance
    
    Método: GET
    Endpoint: /market/price/{symbol}
    
    Parâmetros da URL:
    - symbol (str): Símbolo do par de trading (ex: 'BTCUSDT', 'ETHUSDT')
    
    Retornos:
    - 200: Preço atual do símbolo
    - 400: Símbolo inválido ou erro na API da Binance
    - 500: Erro interno do servidor
    
    Exemplo de uso:
    GET /market/price/BTCUSDT
    
    Resposta esperada:
    {
        "symbol": "BTCUSDT",
        "price": 45000.50
    }
    """
    try:
        # Monta a URL da API pública da Binance para consulta de preço
        binance_url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
        
        # Faz a requisição para a API da Binance
        response = requests.get(binance_url)
        
        # Verifica se a requisição foi bem-sucedida
        if response.status_code != 200:
            return jsonify({
                "error": "Símbolo inválido ou erro na API da Binance",
                "symbol": symbol.upper()
            }), HTTPStatus.BAD_REQUEST
        
        # Extrai dados da resposta da Binance
        price_data = response.json()
        
        # Formata e retorna o resultado
        return jsonify({
            "symbol": price_data["symbol"],
            "price": float(price_data["price"])
        }), HTTPStatus.OK
        
    except requests.RequestException as e:
        return jsonify({
            "error": f"Erro de conexão com a API da Binance: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        return jsonify({
            "error": f"Erro interno ao buscar preço: {str(e)}"
        }), HTTPStatus.INTERNAL_SERVER_ERROR