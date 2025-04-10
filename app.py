from flask import Flask
from database.custom_models import db
from database.schemas import ma
from database.controllers import bp  # seu blueprint
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init DB e Marshmallow
db.init_app(app)
ma.init_app(app)

# Registra as rotas
app.register_blueprint(bp, url_prefix="/api")

# Cria tabelas se não existirem
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
