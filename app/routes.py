import threading
from flask import Blueprint, request, jsonify
from app import db
from app.models import Vaga, Candidato, Inscricao

# Importações dos nossos futuros serviços (Lógica de Negócios)
from app.services.rpa import executar_automacoes_RPA
from app.services.chatbot import gerar_resposta_gemini

# Criação do Blueprint (é como um mini-app para organizar rotas)
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

@api_bp.route('/vagas', methods=['GET'])
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

@api_bp.route('/vagas/<int:id>', methods=['GET'])
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

@api_bp.route('/vagas/<int:id>', methods=['PUT'])
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

@api_bp.route('/vagas/<int:id>', methods=['DELETE'])
def deletar_vaga(id):
    vaga = Vaga.query.get(id)
    if not vaga:
        return jsonify({'erro': 'Vaga não encontrada'}), 404
        
    db.session.delete(vaga)
    db.session.commit()
    return jsonify({'mensagem': 'Vaga deletada com sucesso'}), 200

# ================= CANDIDATOS =================

@api_bp.route('/candidatos', methods=['POST'])
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

# ================= INSCRIÇÕES =================

@api_bp.route('/inscricoes', methods=['POST'])
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

    # Dispara a automação RPA em background chamando o serviço externo
    thread_RPA = threading.Thread(
        target=executar_automacoes_RPA,
        args=(candidato.email, candidato.nome, candidato.telefone, vaga.titulo)
    )
    thread_RPA.start()

    return jsonify({
        'mensagem': 'Inscrição realizada com sucesso! Notificações automáticas em processamento.',
        'id': nova_inscricao.id
    }), 201

# ================= CHATBOT IA =================

@api_bp.route('/chat', methods=['POST'])
def chatbot():
    dados = request.get_json()
    if not dados or 'mensagem' not in dados:
        return jsonify({'erro': 'Mensagem não fornecida.'}), 400
        
    mensagem_usuario = dados['mensagem']
    
    try:
        # Busca vagas e delega o processamento pesado do prompt para o service
        vagas_db = Vaga.query.all()
        resposta_texto = gerar_resposta_gemini(mensagem_usuario, vagas_db)
        
        return jsonify({
            "intencao": "atendimento_bot",
            "resposta": resposta_texto
        }), 200
        
    except Exception as e:
        return jsonify({
            "erro": "Falha ao processar a resposta com a inteligência artificial.", 
            "detalhes": str(e)
        }), 500