import requests

# Dados da vaga que vai aparecer no frontend
nova_vaga = {
    "titulo": "Assistente Administrativo",
    "descricao": "Apoio a processos administrativos, atendimento e planilhas.",
    "area": "Administrativo",
    "modalidade": "Presencial"
}

# Enviando para a sua API (pode usar o localhost ou o link do ngrok)
resposta = requests.post("http://127.0.0.1:5000/vagas", json=nova_vaga)

print(resposta.json())
