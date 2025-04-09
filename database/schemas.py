# Importacao das bibliotecas usadas

from flask_marshmallow import Marshmallow
from custom_models import User, Order, TradeReport

# Definicao de variavel para chamar o Marshmallow e suas funcoes
ma = Marshmallow()

# Schema para a tabela de User
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        incluir_relacao = True
        instance = True

# Schema para a tabela de Order
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        incluir_fk = True
        incluir_relacao = True
        instance = True

# Schema para a tabela de TradeReport
class TradeReportSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TradeReport
        include_fk = True
        instance = True