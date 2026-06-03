from __future__ import annotations

import os
import sys
import time
import threading
import logging
import smtplib
from pathlib import Path
from email.message import EmailMessage
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from pyngrok import ngrok
from dotenv import load_dotenv
import google.generativeai as genai
import pywhatkit

# 1. Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# ====================================================================
# --- MÓDULOS DE AUTOMAÇÃO E LOGS INCORPORADOS ---
# ====================================================================

# --- SETUP DE LOGS ---
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(nome_arquivo: str = "automacao.log") -> logging.Logger:
    logger_name = f"rpa_{nome_arquivo}"
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(LOGS_DIR / nome_arquivo, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

email_logger = get_logger("email.log")
whatsapp_logger = get_logger("whatsapp.log")

# --- FUNÇÕES DE E-MAIL ---
def obter_credenciais() -> tuple[str, str]:
    email_remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")

    if not email_remetente or not senha_app:
        raise ValueError(
            "Defina EMAIL_REMETENTE e EMAIL_SENHA_APP em um arquivo .env."
        )

    return email_remetente, senha_app

def montar_email(destinatario: str, nome: str, vaga: str, empresa: str, link: str | None) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Atualização de candidatura - {vaga}"
    msg["To"] = destinatario

    corpo = (
        f"Olá, {nome},\n\n"
        f"Esta é uma mensagem automática do Portal de Vagas da AV2.\n"
        f"A vaga '{vaga}' na empresa {empresa} está sendo acompanhada pelo sistema.\n"
    )

    if link:
        corpo += f"Link da vaga: {link}\n"

    corpo += "\nMensagem enviada para fins de demonstração da automação com Python.\n"
    msg.set_content(corpo)
    return msg

def enviar_email_smtp(destinatario: str, nome: str, vaga: str, empresa: str, link: str | None) -> None:
    email_remetente, senha_app = obter_credenciais()
    msg = montar_email(destinatario, nome, vaga, empresa, link)
    msg["From"] = email_remetente

    email_logger.info("Iniciando envio de e-mail para %s", destinatario)

    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
        servidor.starttls()
        servidor.login(email_remetente, senha_app)
        servidor.send_message(msg)

    email_logger.info("E-mail enviado com sucesso para %s", destinatario)

# --- FUNÇÕES DE WHATSAPP ---
def validar_numero(numero: str) -> str:
    numero = numero.strip()
    if not numero.startswith("+"):
        raise ValueError("O número deve estar no formato internacional, por exemplo: +5548999999999")
    return numero

def montar_mensagem(nome: str, vaga: str, empresa: str, link: str | None = None) -> str:
    mensagem = (
        f"Olá, {nome}!\n"
        f"A vaga '{vaga}' na empresa {empresa} recebeu uma nova atualização no Portal de Vagas da AV2.\n"
        f"Confira os detalhes e acompanhe a candidatura."
    )
    if link:
        mensagem += f"\nLink: {link}"
    return mensagem

def enviar_whatsapp(numero: str, mensagem: str, esperar: int = 20, fechar_aba: bool = False) -> None:
    whatsapp_logger.info("Iniciando envio de WhatsApp para %s", numero)
    pywhatkit.sendwhatmsg_instantly(
        phone_no=numero,
        message=mensagem,
        wait_time=esperar,
        tab_close=fechar_aba,
        close_time=5,
    )
    time.sleep(3)
    whatsapp_logger.info("Fluxo de envio ao WhatsApp disparado com sucesso para %s", numero)


# ====================================================================
# --- APLICAÇÃO FLASK ---
# ====================================================================

# 2. Configuração do Servidor Flask e Banco de Dados
app = Flask(__name__)

# Configuração de CORS aberto para todas as origens
CORS(app) 

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///portal_vagas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 3. MODELAGEM DAS ENTIDADES OBRIGATÓRIAS ---

class Candidato(db.Model):
    """Modelo para armazenar os dados dos candidatos."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    inscricoes = db.relationship('Inscricao', backref='candidato', lazy=True)

class Vaga(db.Model):
    """Modelo para armazenar as vagas de emprego disponíveis."""
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(50), nullable=False)
    modalidade = db.Column(db.String(50), nullable=False)
    inscricoes = db.relationship('Inscricao', backref='vaga', lazy=True)

class Inscricao(db.Model):
    """Modelo de junção contendo as Chaves Estrangeiras (Foreign Keys)."""
    id = db.Column(db.Integer, primary_key=True)
    data_inscricao = db.Column(db.DateTime, default=datetime.utcnow)
    candidato_id = db.Column(db.Integer, db.ForeignKey('candidato.id'), nullable=False)
    vaga_id = db.Column(db.Integer, db.ForeignKey('vaga.id'), nullable=False)

# 4. Inicialização e Criação do Banco Local com Carga Inicial (Seed)
with app.app_context():
    db.create_all()
    
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

# --- 5. ENDPOINTS CRUD (API RESTful) ---

@app.route('/', methods=['GET'])
def health_check():
    """Rota raiz necessária para o botão 'Testar conexão' do frontend."""
    return jsonify({
        'status': 'Online',
        'mensagem': 'Conexão com a API realizada com sucesso!'
    }), 200

# ================= VAGAS =================

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

@app.route('/vagas', methods=['GET'])
def listar_vagas():
    vagas = Vaga.query.all()
    resultado = [{
        'id': vaga.id,
        'titulo': vaga.titulo,
        'descricao': vaga.descricao,
        'area': vaga.area,
        'modalidade': vaga.modalidade
    } for vaga in vagas]
    return jsonify(resultado), 200

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

@app.route('/vagas/<int:id>', methods=['PUT'])
def atualizar_vaga(id):
    vaga = Vaga.query.get(id)
    if not vaga:
        return jsonify({'erro': 'Vaga não encontrada'}), 404
        
    dados = request.get_json()
    if 'titulo' in dados: vaga.titulo = dados['titulo']
    if 'descricao' in dados: vaga.descricao = dados['descricao']
    if 'area' in dados: vaga.area = dados['area']
    if 'modalidade' in dados: vaga.modalidade = dados['modalidade']
        
    db.session.commit()
    return jsonify({'mensagem': 'Vaga atualizada com sucesso'}), 200

@app.route('/vagas/<int:id>', methods=['DELETE'])
def deletar_vaga(id):
    vaga = Vaga.query.get(id)
    if not vaga:
        return jsonify({'erro': 'Vaga não encontrada'}), 404
        
    db.session.delete(vaga)
    db.session.commit()
    return jsonify({'mensagem': 'Vaga deletada com sucesso'}), 200

# ================= CANDIDATOS =================

@app.route('/candidatos', methods=['POST'])
def criar_candidato():
    dados = request.get_json()
    if not dados or 'nome' not in dados or 'email' not in dados:
        return jsonify({'erro': 'Nome e email são obrigatórios.'}), 400
        
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


# ================= INSCRIÇÕES COM AUTOMAÇÃO =================

# --- FUNÇÃO AUXILIAR EM SEGUNDO PLANO ---
def executar_automacoes_RPA(email, nome, telefone, titulo_vaga):
    """Executa o envio de e-mail e whatsapp sem bloquear o Flask."""
    # 1. Tentativa de envio do E-mail
    try:
        enviar_email_smtp(
            destinatario=email,
            nome=nome,
            vaga=titulo_vaga,
            empresa="Portal de Vagas AV2",
            link=None
        )
    except Exception as e:
        email_logger.error(f"[RPA ERRO] Falha no envio de e-mail: {e}")
        print(f"[RPA ERRO] Falha no envio de e-mail: {e}")

    # 2. Tentativa de envio do WhatsApp
    try:
        if telefone and telefone != 'Não informado':
            numero_formatado = telefone if telefone.startswith('+') else f"+55{telefone}"

            mensagem = montar_mensagem(
                nome=nome,
                vaga=titulo_vaga,
                empresa="Portal de Vagas AV2",
                link=None
            )
            enviar_whatsapp(numero=numero_formatado, mensagem=mensagem, esperar=20, fechar_aba=True)
    except Exception as e:
        whatsapp_logger.error(f"[RPA ERRO] Falha no fluxo do WhatsApp Web: {e}")
        print(f"[RPA ERRO] Falha no fluxo do WhatsApp Web: {e}")


@app.route('/inscricoes', methods=['POST'])
def criar_inscricao():
    dados = request.get_json()
    if not dados or 'candidato_id' not in dados or 'vaga_id' not in dados:
        return jsonify({'erro': 'IDs do candidato e da vaga são obrigatórios.'}), 400

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

    thread_RPA = threading.Thread(
        target=executar_automacoes_RPA,
        args=(candidato.email, candidato.nome, candidato.telefone, vaga.titulo)
    )
    thread_RPA.start()

    return jsonify({
        'mensagem': 'Inscrição realizada com sucesso! Notificações automáticas em processamento.',
        'id': nova_inscricao.id
    }), 201


# --- 6. CHATBOT E INTELIGÊNCIA ARTIFICIAL ---

gemini_key = os.getenv('GEMINI_API_KEY', 'SUA_CHAVE_API_AQUI')
genai.configure(api_key=gemini_key)
modelo_ia = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/chat', methods=['POST'])
def chatbot():
    dados = request.get_json()
    if not dados or 'mensagem' not in dados:
        return jsonify({'erro': 'Mensagem não fornecida.'}), 400
        
    mensagem_usuario = dados['mensagem'].lower()
    
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
        
    else:
        try:
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
    port = int(os.getenv('FLASK_PORT', 5000))
    
    ngrok_token = os.getenv('NGROK_AUTH_TOKEN')
    ngrok_domain = os.getenv('NGROK_DOMAIN')
    
    if ngrok_token:
        ngrok.set_auth_token(ngrok_token)
    
    if ngrok_domain:
        public_url = ngrok.connect(port, domain=ngrok_domain).public_url
    else:
        public_url = ngrok.connect(port).public_url
        
    print(f"\n * Túnel Ngrok ativo! Acesse sua API por aqui: {public_url}\n")
    
    app.run(debug=True, port=port, use_reloader=False)
