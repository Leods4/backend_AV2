from app import db
from app.models import Candidato

def criar_candidato(dados):
    if not dados or 'nome' not in dados or 'email' not in dados:
        return {'erro': 'Nome e email são obrigatórios.'}, 400
        
    if Candidato.query.filter_by(email=dados['email']).first():
        return {'erro': 'Este e-mail já está cadastrado.'}, 400
        
    novo_candidato = Candidato(
        nome=dados['nome'],
        email=dados['email'],
        telefone=dados.get('telefone', 'Não informado')
    )
    db.session.add(novo_candidato)
    db.session.commit()
    return {'mensagem': 'Candidato criado com sucesso!', 'id': novo_candidato.id}, 201

def listar_candidatos():
    candidatos = Candidato.query.all()
    resultado = [{
        'id': c.id,
        'nome': c.nome,
        'email': c.email,
        'telefone': c.telefone
    } for c in candidatos]
    return resultado, 200

def buscar_candidato(id):
    candidato = Candidato.query.get(id)
    if not candidato:
        return {'erro': 'Candidato não encontrado'}, 404
    return {
        'id': candidato.id,
        'nome': candidato.nome,
        'email': candidato.email,
        'telefone': candidato.telefone
    }, 200

def atualizar_candidato(id, dados):
    candidato = Candidato.query.get(id)
    if not candidato:
        return {'erro': 'Candidato não encontrado'}, 404
        
    if 'email' in dados and dados['email'] != candidato.email:
        if Candidato.query.filter_by(email=dados['email']).first():
             return {'erro': 'Este e-mail já está cadastrado por outro usuário.'}, 400
        candidato.email = dados['email']
        
    if 'nome' in dados: candidato.nome = dados['nome']
    if 'telefone' in dados: candidato.telefone = dados['telefone']
        
    db.session.commit()
    return {'mensagem': 'Candidato atualizado com sucesso'}, 200

def deletar_candidato(id):
    candidato = Candidato.query.get(id)
    if not candidato:
        return {'erro': 'Candidato não encontrado'}, 404
        
    try:
        db.session.delete(candidato)
        db.session.commit()
        return {'mensagem': 'Candidato deletado com sucesso'}, 200
    except Exception as e:
        db.session.rollback()
        return {
            'erro': 'Não foi possível deletar o candidato. Verifique se ele possui inscrições ativas.', 
            'detalhes': str(e)
        }, 400