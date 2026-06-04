from app import db
from app.models import Vaga

def criar_vaga(dados):
    if not dados or 'titulo' not in dados or 'descricao' not in dados:
        return {'erro': 'Dados incompletos. Titulo e descricao são obrigatórios.'}, 400
        
    nova_vaga = Vaga(
        titulo=dados['titulo'],
        descricao=dados['descricao'],
        area=dados.get('area', 'Não especificada'),
        modalidade=dados.get('modalidade', 'Não especificada')
    )
    db.session.add(nova_vaga)
    db.session.commit()
    return {'mensagem': 'Vaga criada com sucesso!', 'id': nova_vaga.id}, 201

def listar_vagas():
    vagas = Vaga.query.all()
    resultado = [{
        'id': vaga.id,
        'titulo': vaga.titulo,
        'descricao': vaga.descricao,
        'area': vaga.area,
        'modalidade': vaga.modalidade
    } for vaga in vagas]
    return resultado, 200

def buscar_vaga(id):
    vaga = Vaga.query.get(id)
    if not vaga:
        return {'erro': 'Vaga não encontrada'}, 404
    return {
        'id': vaga.id,
        'titulo': vaga.titulo,
        'descricao': vaga.descricao,
        'area': vaga.area,
        'modalidade': vaga.modalidade
    }, 200

def atualizar_vaga(id, dados):
    vaga = Vaga.query.get(id)
    if not vaga:
        return {'erro': 'Vaga não encontrada'}, 404
        
    if 'titulo' in dados: vaga.titulo = dados['titulo']
    if 'descricao' in dados: vaga.descricao = dados['descricao']
    if 'area' in dados: vaga.area = dados['area']
    if 'modalidade' in dados: vaga.modalidade = dados['modalidade']
        
    db.session.commit()
    return {'mensagem': 'Vaga atualizada com sucesso'}, 200

def deletar_vaga(id):
    vaga = Vaga.query.get(id)
    if not vaga:
        return {'erro': 'Vaga não encontrada'}, 404
        
    db.session.delete(vaga)
    db.session.commit()
    return {'mensagem': 'Vaga deletada com sucesso'}, 200