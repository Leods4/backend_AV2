from datetime import datetime
from app import db # Importaremos a instância do banco do nosso app

class Candidato(db.Model):
    """Modelo para armazenar os dados dos candidatos."""
    __tablename__ = 'candidato'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    inscricoes = db.relationship('Inscricao', backref='candidato', lazy=True)

class Vaga(db.Model):
    """Modelo para armazenar as vagas de emprego disponíveis."""
    __tablename__ = 'vaga'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(50), nullable=False)
    modalidade = db.Column(db.String(50), nullable=False)
    inscricoes = db.relationship('Inscricao', backref='vaga', lazy=True)

class Inscricao(db.Model):
    """Modelo de junção contendo as Chaves Estrangeiras (Foreign Keys)."""
    __tablename__ = 'inscricao'
    
    id = db.Column(db.Integer, primary_key=True)
    data_inscricao = db.Column(db.DateTime, default=datetime.utcnow)
    candidato_id = db.Column(db.Integer, db.ForeignKey('candidato.id'), nullable=False)
    vaga_id = db.Column(db.Integer, db.ForeignKey('vaga.id'), nullable=False)