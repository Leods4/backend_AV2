from flask import Blueprint, request, jsonify
from app.models import Vaga

# Importação dos novos sub-serviços estruturados
from app.services import vaga_service, candidato_service, inscricao_service
from app.services.chatbot import gerar_resposta_gemini

api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def health_check():
    """Rota raiz necessária para o botão 'Testar conexão' do frontend."""
    return jsonify({
        'status': 'Online',
        'mensagem': 'Conexão com a API realizada com sucesso!'
    }), 200


# ================= VAGAS =================

@api_bp.route('/vagas', methods=['POST'])
def criar_vaga():
    resposta, status = vaga_service.criar_vaga(request.get_json())
    return jsonify(resposta), status

@api_bp.route('/vagas', methods=['GET'])
def listar_vagas():
    resposta, status = vaga_service.listar_vagas()
    return jsonify(resposta), status

@api_bp.route('/vagas/<int:id>', methods=['GET'])
def buscar_vaga(id):
    resposta, status = vaga_service.buscar_vaga(id)
    return jsonify(resposta), status

@api_bp.route('/vagas/<int:id>', methods=['PUT'])
def atualizar_vaga(id):
    resposta, status = vaga_service.atualizar_vaga(id, request.get_json())
    return jsonify(resposta), status

@api_bp.route('/vagas/<int:id>', methods=['DELETE'])
def deletar_vaga(id):
    resposta, status = vaga_service.deletar_vaga(id)
    return jsonify(resposta), status


# ================= CANDIDATOS =================

@api_bp.route('/candidatos', methods=['POST'])
def criar_candidato():
    resposta, status = candidato_service.criar_candidato(request.get_json())
    return jsonify(resposta), status

@api_bp.route('/candidatos', methods=['GET'])
def listar_candidatos():
    resposta, status = candidato_service.listar_candidatos()
    return jsonify(resposta), status

@api_bp.route('/candidatos/<int:id>', methods=['GET'])
def buscar_candidato(id):
    resposta, status = candidato_service.buscar_candidato(id)
    return jsonify(resposta), status

@api_bp.route('/candidatos/<int:id>', methods=['PUT'])
def atualizar_candidato(id):
    resposta, status = candidato_service.atualizar_candidato(id, request.get_json())
    return jsonify(resposta), status

@api_bp.route('/candidatos/<int:id>', methods=['DELETE'])
def deletar_candidato(id):
    resposta, status = candidato_service.deletar_candidato(id)
    return jsonify(resposta), status


# ================= INSCRIÇÕES =================

@api_bp.route('/inscricoes', methods=['POST'])
def criar_inscricao():
    resposta, status = inscricao_service.criar_inscricao(request.get_json())
    return jsonify(resposta), status

@api_bp.route('/inscricoes', methods=['GET'])
def listar_inscricoes():
    resposta, status = inscricao_service.listar_inscricoes()
    return jsonify(resposta), status

@api_bp.route('/inscricoes/<int:id>', methods=['GET'])
def buscar_inscricao(id):
    resposta, status = inscricao_service.buscar_inscricao(id)
    return jsonify(resposta), status

@api_bp.route('/inscricoes/<int:id>', methods=['PUT'])
def atualizar_inscricao(id):
    resposta, status = inscricao_service.atualizar_inscricao(id, request.get_json())
    return jsonify(resposta), status

@api_bp.route('/inscricoes/<int:id>', methods=['DELETE'])
def deletar_inscricao(id):
    resposta, status = inscricao_service.deletar_inscricao(id)
    return jsonify(resposta), status


# ================= CHATBOT IA =================

@api_bp.route('/chat', methods=['POST'])
def chatbot():
    dados = request.get_json()
    if not dados or 'mensagem' not in dados:
        return jsonify({'erro': 'Mensagem não fornecida.'}), 400
        
    mensagem_usuario = dados['mensagem']
    
    try:
        vagas_db = Vaga.query.all()
        # Agora recebemos um dicionário com 'resposta' e 'intencao' da IA
        resultado_ia = gerar_resposta_gemini(mensagem_usuario, vagas_db)
        
        return jsonify({
            "intencao": resultado_ia.get("intencao", "atendimento_bot"),
            "resposta": resultado_ia.get("resposta", "Não consegui processar sua mensagem.")
        }), 200
        
    except Exception as e:
        return jsonify({
            "erro": "Falha ao processar a resposta com a inteligência artificial.", 
            "detalhes": str(e)
        }), 500
