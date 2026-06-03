from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Importação do CORS adicionada
from datetime import datetime
import google.generativeai as genai
import os
from pyngrok import ngrok # Importação do ngrok adicionada

# 1. Configuração do Servidor Flask e Banco de Dados SQLite local
app = Flask(__name__)

# Configuração de CORS aberto para todas as origens
CORS(app) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal_vagas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. MODELAGEM DAS ENTIDADES OBRIGATÓRIAS ---

class Candidato(db.Model):
    """Modelo para armazenar os dados dos candidatos."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    
    # Relacionamento com as inscrições
    inscricoes = db.relationship('Inscricao', backref='candidato', lazy=True)

class Vaga(db.Model):
    """Modelo para armazenar as vagas de emprego disponíveis."""
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(50), nullable=False)
    modalidade = db.Column(db.String(50), nullable=False)
    
    # Relacionamento com as inscrições
    inscricoes = db.relationship('Inscricao', backref='vaga', lazy=True)

class Inscricao(db.Model):
    """Modelo de junção contendo as Chaves Estrangeiras (Foreign Keys)."""
    id = db.Column(db.Integer, primary_key=True)
    data_inscricao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chaves Estrangeiras ligando o Candidato à Vaga
    candidato_id = db.Column(db.Integer, db.ForeignKey('candidato.id'), nullable=False)
    vaga_id = db.Column(db.Integer, db.ForeignKey('vaga.id'), nullable=False)

# 3. Inicialização e Criação do Banco Local
with app.app_context():
    db.create_all() # Cria o arquivo portal_vagas.db e as tabelas, se não existirem

# --- 4. ENDPOINTS CRUD (API RESTful) ---

# ================= VAGAS =================

# Criar uma nova vaga (POST)
@app.route('/vagas', methods=['POST'])
def criar_vaga():
    dados = request.get_json()
    
    if not dados or 'titulo' not in dados or 'descricao' not in dados:
        return jsonify({'erro': 'Dados incompletos. Titulo e descricao são obrigatórios.'}), 400
        
    nova_vaga = Vaga(
        titulo=dados['titulo'],
        descricao=dados['descricao'],
        area=dados.get('area', 'Não especificada'),
        modalidade=dados.get('modalidade', 'Não especificada')
    )
    
    db.session.add(nova_vaga)
    db.session.commit()
    
    return jsonify({'mensagem': 'Vaga criada com sucesso!', 'id': nova_vaga.id}), 201

# Listar todas as vagas (GET)
@app.route('/vagas', methods=['GET'])
def listar_vagas():
    vagas = Vaga.query.all()
    resultado = []
    
    for vaga in vagas:
        resultado.append({
            'id': vaga.id,
            'titulo': vaga.titulo,
            'descricao': vaga.descricao,
            'area': vaga.area,
            'modalidade': vaga.modalidade
        })
        
    return jsonify(resultado), 200

# Buscar uma vaga específica pelo ID (GET)
@app.route('/vagas/<int:id>', methods=['GET'])
def buscar_vaga(id):
    vaga = Vaga.query.get(id)
    
    if not vaga:
        return jsonify({'erro': 'Vaga não encontrada'}), 404
        
    return jsonify({
        'id': vaga.id,
        'titulo': vaga.titulo,
        'descricao': vaga.descricao,
        'area': vaga.area,
        'modalidade': vaga.modalidade
    }), 200

# Atualizar uma vaga (PUT)
@app.route('/vagas/<int:id>', methods=['PUT'])
def atualizar_vaga(id):
    vaga = Vaga.query.get(id)
    
    if not vaga:
        return jsonify({'erro': 'Vaga não encontrada'}), 404
        
    dados = request.get_json()
    
    if 'titulo' in dados:
        vaga.titulo = dados['titulo']
    if 'descricao' in dados:
        vaga.descricao = dados['descricao']
    if 'area' in dados:
        vaga.area = dados['area']
    if 'modalidade' in dados:
        vaga.modalidade = dados['modalidade']
        
    db.session.commit()
    return jsonify({'mensagem': 'Vaga atualizada com sucesso'}), 200

# Deletar uma vaga (DELETE)
@app.route('/vagas/<int:id>', methods=['DELETE'])
def deletar_vaga(id):
    vaga = Vaga.query.get(id)
    
    if not vaga:
        return jsonify({'erro': 'Vaga não encontrada'}), 404
        
    db.session.delete(vaga)
    db.session.commit()
    
    return jsonify({'mensagem': 'Vaga deletada com sucesso'}), 200

# ================= CANDIDATOS =================

# Criar um novo candidato (POST)
@app.route('/candidatos', methods=['POST'])
def criar_candidato():
    dados = request.get_json()
    
    if not dados or 'nome' not in dados or 'email' not in dados:
        return jsonify({'erro': 'Nome e email são obrigatórios.'}), 400
        
    # Previne e-mails duplicados
    if Candidato.query.filter_by(email=dados['email']).first():
        return jsonify({'erro': 'Este e-mail já está cadastrado.'}), 400
        
    novo_candidato = Candidato(
        nome=dados['nome'],
        email=dados['email'],
        telefone=dados.get('telefone', 'Não informado')
    )
    
    db.session.add(novo_candidato)
    db.session.commit()
    
    return jsonify({'mensagem': 'Candidato criado com sucesso!', 'id': novo_candidato.id}), 201

# ================= INSCRIÇÕES =================

# Realizar uma inscrição relacionando candidato e vaga (POST)
@app.route('/inscricoes', methods=['POST'])
def criar_inscricao():
    dados = request.get_json()
    
    if not dados or 'candidato_id' not in dados or 'vaga_id' not in dados:
        return jsonify({'erro': 'IDs do candidato e da vaga são obrigatórios.'}), 400
        
    # Verifica se os IDs existem no banco de dados
    candidato = Candidato.query.get(dados['candidato_id'])
    vaga = Vaga.query.get(dados['vaga_id'])
    
    if not candidato:
        return jsonify({'erro': 'Candidato não encontrado.'}), 404
    if not vaga:
        return jsonify({'erro': 'Vaga não encontrada.'}), 404
        
    nova_inscricao = Inscricao(
        candidato_id=dados['candidato_id'],
        vaga_id=dados['vaga_id']
    )
    
    db.session.add(nova_inscricao)
    db.session.commit()
    
    return jsonify({'mensagem': 'Inscrição realizada com sucesso!', 'id': nova_inscricao.id}), 201

# --- 5. CHATBOT E INTELIGÊNCIA ARTIFICIAL ---

# Configuração da API do Gemini (Substitua pela sua chave real)
genai.configure(api_key="SUA_CHAVE_API_AQUI")
modelo_ia = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/chat', methods=['POST'])
def chatbot():
    dados = request.get_json()
    
    if not dados or 'mensagem' not in dados:
        return jsonify({'erro': 'Mensagem não fornecida.'}), 400
        
    mensagem_usuario = dados['mensagem'].lower()
    
    # 1. Reconhecimento de Intenções (Fluxo Lógico do Banco de Dados)
    if "vaga" in mensagem_usuario or "filtro" in mensagem_usuario:
        return jsonify({
            "intencao": "consulta_vagas",
            "resposta": "Entendi que você quer explorar nossas vagas! O frontend agora pode acionar a rota GET /vagas para te mostrar as opções."
        }), 200
        
    elif "candidatar" in mensagem_usuario or "inscrição" in mensagem_usuario:
        return jsonify({
            "intencao": "candidatura",
            "resposta": "Ótimo! Para prosseguir com a candidatura, precisarei dos seus dados. O frontend deve acionar a rota POST /inscricoes."
        }), 200
        
    # 2. Respostas Abertas (Fallback para o Gemini)
    else:
        try:
            # Prompt de sistema para dar contexto à IA antes dela responder
            prompt_contexto = f"Você é o assistente virtual de um portal de vagas de emprego. Responda de forma educada, prestativa e sucinta à seguinte mensagem: {dados['mensagem']}"
            
            resposta_gemini = modelo_ia.generate_content(prompt_contexto)
            
            return jsonify({
                "intencao": "pergunta_geral",
                "resposta": resposta_gemini.text
            }), 200
            
        except Exception as e:
            return jsonify({
                "erro": "Falha ao processar a resposta com a inteligência artificial.", 
                "detalhes": str(e)
            }), 500
        
if __name__ == '__main__':
    port = 5000
    
    # Abre o túnel do ngrok na porta especificada
    public_url = ngrok.connect(port).public_url
    print(f" * Túnel Ngrok ativo! Acesse sua API por aqui: {public_url}")
    
    # Executa a aplicação. use_reloader=False é crucial aqui para evitar erros de limite de conexões do ngrok.
    app.run(debug=True, port=port, use_reloader=False)
