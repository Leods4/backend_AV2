import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 1. Inicializamos as extensões fora da função.
# Isso permite que arquivos como 'models.py' e 'routes.py' importem o 'db' sem problemas.
db = SQLAlchemy()
cors = CORS()

def create_app():
    """Função Fábrica (Factory) que cria e configura a aplicação Flask."""
    app = Flask(__name__)
    
    # 2. Configurações do Banco de Dados (vêm do ambiente ou usam o padrão SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///../portal_vagas.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 3. Vincula as extensões ao aplicativo criado
    db.init_app(app)
    cors.init_app(app) # Permite o acesso do seu frontend
    
    # 4. Registra as Rotas (Blueprint)
    # Importamos aqui dentro para garantir que o 'db' já foi criado antes das rotas tentarem usá-lo
    from app.routes import api_bp
    app.register_blueprint(api_bp)
    
    # 5. Inicialização do Banco de Dados e Carga Inicial (Seed)
    with app.app_context():
        db.create_all()
        
        # Importamos o modelo aqui dentro para o seed
        from app.models import Vaga
        
        # Adiciona vagas de teste caso o banco esteja completamente vazio
        if Vaga.query.count() == 0:
            vagas_teste = [
                Vaga(titulo="Desenvolvedor Frontend", descricao="Vaga para dev React/JS", area="Tecnologia", modalidade="Remoto"),
                Vaga(titulo="Analista de Dados", descricao="Vaga para análise de dados com Python", area="Dados", modalidade="Híbrido"),
                Vaga(titulo="Desenvolvedor Backend", descricao="Vaga para desenvolvimento de APIs com Flask", area="Tecnologia", modalidade="Remoto")
            ]
            db.session.bulk_save_objects(vagas_teste)
            db.session.commit()
            print(" -> Carga inicial de vagas inserida com sucesso no banco de dados!")
            
    return app