import os
import json
from google import genai

def obter_cliente_gemini():
    """Inicializa e retorna o cliente do Gemini usando a chave de ambiente."""
    gemini_key = os.getenv('GEMINI_API_KEY', 'SUA_CHAVE_API_AQUI')
    return genai.Client(api_key=gemini_key)

def gerar_resposta_gemini(mensagem_usuario: str, vagas_db: list) -> dict:
    """
    Recebe a mensagem do usuário e a lista de vagas do banco de dados,
    monta o prompt de contexto (guardrails) e retorna um dicionário com a resposta e a intenção.
    """
    client = obter_cliente_gemini()
    
    lista_vagas = "\n".join([
        f"- {v.titulo} ({v.area} / {v.modalidade}): {v.descricao}" 
        for v in vagas_db
    ])
    
    prompt_contexto = f"""Você é o assistente virtual recrutador do Portal de Vagas da AV2. 
    Sua missão é ajudar os candidatos a encontrarem vagas e tirarem dúvidas.
    
    AQUI ESTÃO AS VAGAS DISPONÍVEIS ATUALMENTE NO BANCO DE DADOS:
    {lista_vagas if lista_vagas else "Nenhuma vaga disponível no momento."}
    
    INSTRUÇÕES DE COMPORTAMENTO:
    - Seja educado, prestativo e sucinto em suas respostas.
    - Se o usuário perguntar sobre vagas, recomende as que estão na lista.
    - Não invente vagas que não estão na lista acima em nenhuma circunstância.
    - Assuntos fora de vagas e carreiras da AV2 devem ser recusados educadamente.
    
    INSTRUÇÕES DE FORMATO DE SAÍDA (CRÍTICO):
    Você deve responder EXCLUSIVAMENTE em formato JSON válido, contendo exatamente estas duas chaves:
    1. "resposta": Sua resposta em texto formulada para o usuário.
    2. "intencao": Classifique a intenção do usuário em APENAS UMA das seguintes opções:
       - "consulta_vagas" -> Se o usuário quer saber quais vagas existem, busca oportunidades ou pergunta o que tem disponível.
       - "candidatura" -> Se o usuário diz que quer se inscrever, candidatar-se ou pergunta como enviar currículo para uma vaga específica.
       - "atendimento_bot" -> Para saudações, despedidas ou conversas gerais fora das duas intenções acima.
    
    Mensagem do usuário: {mensagem_usuario}"""
    
    resposta_gemini = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt_contexto
    )
    
    # Extrai o texto e limpa possíveis formatações markdown (```json ... ```)
    texto_limpo = resposta_gemini.text.strip().removeprefix("```json").removesuffix("```").strip()
    
    try:
        # Converte a string JSON da IA para um dicionário Python
        resultado = json.loads(texto_limpo)
        return resultado
    except json.JSONDecodeError:
        # Fallback de segurança caso a IA não retorne um JSON perfeito
        return {
            "resposta": resposta_gemini.text,
            "intencao": "atendimento_bot"
        }
