import os
from google import genai

def obter_cliente_gemini():
    """Inicializa e retorna o cliente do Gemini usando a chave de ambiente."""
    gemini_key = os.getenv('GEMINI_API_KEY', 'SUA_CHAVE_API_AQUI')
    return genai.Client(api_key=gemini_key)

def gerar_resposta_gemini(mensagem_usuario: str, vagas_db: list) -> str:
    """
    Recebe a mensagem do usuário e a lista de vagas do banco de dados,
    monta o prompt de contexto (guardrails) e retorna a resposta da IA.
    """
    client = obter_cliente_gemini()
    
    # 1. Prepara as vagas reais do banco para injetar no contexto da IA
    lista_vagas = "\n".join([
        f"- {v.titulo} ({v.area} / {v.modalidade}): {v.descricao}" 
        for v in vagas_db
    ])
    
    # 2. Constrói o super-prompt limitando a atuação do assistente
    prompt_contexto = f"""Você é o assistente virtual recrutador do Portal de Vagas da AV2. 
    Sua missão é ajudar os candidatos a encontrarem vagas e tirarem dúvidas.
    
    AQUI ESTÃO AS VAGAS DISPONÍVEIS ATUALMENTE NO BANCO DE DADOS:
    {lista_vagas if lista_vagas else "Nenhuma vaga disponível no momento."}
    
    INSTRUÇÕES:
    - Seja educado, prestativo e sucinto em suas respostas.
    - Se o usuário perguntar sobre vagas, recomende as que estão na lista acima detalhando de forma atrativa.
    - Se o usuário quiser se candidatar, oriente-o a preencher o formulário no site ou navegar pelo sistema.
    - Não invente vagas que não estão na lista acima em nenhuma circunstância.
    - Se o usuário perguntar sobre qualquer assunto que não seja carreira, vagas de emprego ou processos seletivos da AV2, recuse-se educadamente a responder e redirecione a conversa para as vagas de emprego.
    
    Mensagem do usuário: {mensagem_usuario}"""
    
    # 3. Gera a resposta e retorna apenas o texto
    resposta_gemini = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt_contexto
    )
    
    return resposta_gemini.text