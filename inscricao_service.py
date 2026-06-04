import threading
from app import db
from app.models import Inscricao, Candidato, Vaga
from app.services.rpa import executar_automacoes_RPA

def criar_inscricao(dados):
    if not dados or 'candidato_id' not in dados or 'vaga_id' not in dados:
        return {'erro': 'IDs do candidato e da vaga são obrigatórios.'}, 400

    candidato = Candidato.query.get(dados['candidato_id'])
    vaga = Vaga.query.get(dados['vaga_id'])

    if not candidato:
        return {'erro': 'Candidato não encontrado.'}, 404
    if not vaga:
        return {'erro': 'Vaga não encontrada.'}, 404

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

    return {
        'mensagem': 'Inscrição realizada com sucesso! Notificações automáticas em processamento.',
        'id': nova_inscricao.id
    }, 201

def listar_inscricoes():
    inscricoes = Inscricao.query.all()
    resultado = [{
        'id': i.id,
        'data_inscricao': i.data_inscricao.isoformat() if i.data_inscricao else None,
        'candidato_id': i.candidato_id,
        'vaga_id': i.vaga_id
    } for i in inscricoes]
    return resultado, 200

def buscar_inscricao(id):
    inscricao = Inscricao.query.get(id)
    if not inscricao:
        return {'erro': 'Inscrição não encontrada'}, 404
    return {
        'id': inscricao.id,
        'data_inscricao': inscricao.data_inscricao.isoformat() if inscricao.data_inscricao else None,
        'candidato_id': inscricao.candidato_id,
        'vaga_id': inscricao.vaga_id
    }, 200

def atualizar_inscricao(id, dados):
    inscricao = Inscricao.query.get(id)
    if not inscricao:
        return {'erro': 'Inscrição não encontrada'}, 404
        
    if 'candidato_id' in dados:
        if not Candidato.query.get(dados['candidato_id']):
            return {'erro': 'Novo Candidato informado não existe.'}, 404
        inscricao.candidato_id = dados['candidato_id']
        
    if 'vaga_id' in dados:
        if not Vaga.query.get(dados['vaga_id']):
            return {'erro': 'Nova Vaga informada não existe.'}, 404
        inscricao.vaga_id = dados['vaga_id']
        
    db.session.commit()
    return {'mensagem': 'Inscrição atualizada com sucesso'}, 200

def deletar_inscricao(id):
    inscricao = Inscricao.query.get(id)
    if not inscricao:
        return {'erro': 'Inscrição não encontrada'}, 404
        
    db.session.delete(inscricao)
    db.session.commit()
    return {'mensagem': 'Inscrição deletada com sucesso'}, 200