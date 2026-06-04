# 🚀 API Portal de Vagas AV2

Uma API RESTful desenvolvida em Flask para gerenciamento de vagas de emprego, candidatos e inscrições, estruturada sob a divisão de responsabilidades entre **Rotas** e **Serviços (Services)** para garantir alta escalabilidade, testes facilitados e manutenção modular.

O projeto inclui funcionalidades avançadas, como:
- **Automação RPA:** Disparo de notificações via WhatsApp (PyWhatKit) e E-mail (SMTP) em segundo plano.
- **Inteligência Artificial:** Chatbot integrado ao Google Gemini (via API oficial) para atendimento inteligente aos candidatos.
- **Túnel Público Dinâmico:** Integração nativa com Ngrok para exposição imediata da API local para a internet.

---

## 📁 Estrutura de Diretórios (Rotas & Serviços)

O código foi componentizado em serviços dedicados para cada entidade do banco de dados, deixando o arquivo de rotas limpo e focado em HTTP:

```text
portal_vagas_api/
│
├── app/                      # Aplicação Flask (Pacote principal)
│   ├── __init__.py           # Factory Function: Configura o App, BD e CORS
│   ├── models.py             # (Models) Classes do SQLAlchemy (Vaga, Candidato, Inscricao)
│   ├── routes.py             # (Router/Endpoints) Recebe requisições e delega para os serviços
│   │
│   └── services/             # Camada de Regras de Negócio (Lógica Isolada)
│       ├── vaga_service.py       # CRUD completo e manipulação de Vagas
│       ├── candidato_service.py  # CRUD completo e validações de Candidatos
│       ├── inscricao_service.py  # CRUD completo, validações de chaves e disparo RPA
│       ├── rpa.py                # Orquestração assíncrona do E-mail e WhatsApp
│       └── chatbot.py            # Configuração do Client e Prompts do Google Gemini
│
├── logs/                     # Diretório gerado automaticamente para os logs (RPA)
├── .env                      # Variáveis de ambiente (Credenciais e Configurações)
└── run.py                    # Ponto de entrada: Inicializa o Ngrok e executa o servidor
```

---

## 🛠 Pré-requisitos

Para rodar este projeto, você precisará do **Python 3.10+** instalado em sua máquina.

As dependências principais são:
* Flask & Flask-SQLAlchemy (Backend e Banco de Dados)
* Flask-CORS (Comunicação com o Frontend)
* PyWhatKit & smtplib (Automações RPA)
* `google-genai` (SDK oficial atualizado do Gemini)
* PyNgrok (Túneis de rede)
* Python-dotenv (Gerenciamento de variáveis)

---

## ⚙️ Configuração do Ambiente

### 1. Clonar e preparar o ambiente
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd portal_vagas_api
python -m venv venv

# Ative o ambiente virtual (Windows)
venv\Scripts\activate

# Ative o ambiente virtual (Linux/Mac)
source venv/bin/activate
```

### 2. Instalar as Dependências
```bash
pip install Flask Flask-SQLAlchemy Flask-Cors pywhatkit python-dotenv pyngrok google-genai
```

### 3. Configurar Variáveis de Ambiente (`.env`)
Crie um arquivo chamado `.env` na raiz do projeto (mesmo nível do `run.py`) e insira as suas credenciais:

```env
# Banco de Dados
DATABASE_URL=sqlite:///../portal_vagas.db
FLASK_PORT=5000

# IA - Google Gemini
GEMINI_API_KEY=sua_chave_de_api_gemini_aqui

# Automação de E-mail (Requer senha de aplicativo do Gmail)
EMAIL_REMETENTE=seu_email@gmail.com
EMAIL_SENHA_APP=sua_senha_de_aplicativo_aqui

# Túnel Ngrok (Opcional, mas recomendado)
NGROK_AUTH_TOKEN=seu_token_ngrok_aqui
```
> **Nota sobre o E-mail:** A senha de app do Gmail exige que a Autenticação de 2 Fatores esteja ativada na sua conta Google.

---

## ▶️ Como Executar

Com o ambiente virtual ativado e o `.env` configurado, basta rodar o arquivo principal:

```bash
python run.py
```

No console, você verá que o servidor Flask iniciou e o Ngrok gerou uma URL pública (ex: `https://abcd-123.ngrok-free.app`). Use essa URL para testar os endpoints ou conectar o seu frontend.

> **Primeira execução:** O banco de dados SQLite (`portal_vagas.db`) será criado automaticamente, e uma carga inicial de vagas (Seed) será inserida para facilitar os testes!

---

## 📡 Endpoints Principais (CRUD Completo)

Todas as rotas HTTP abaixo delegam o processamento de dados e o controle de status diretamente para seus respectivos arquivos na pasta `services`.

### 📌 Vagas (`/vagas`)
* `GET /vagas`: Lista todas as vagas registradas.
* `POST /vagas`: Cria uma nova vaga (Exige: `titulo`, `descricao`).
* `GET /vagas/<id>`: Busca os detalhes de uma vaga específica.
* `PUT /vagas/<id>`: Atualiza os dados de uma vaga existente.
* `DELETE /vagas/<id>`: Remove uma vaga do sistema.

### 📌 Candidatos (`/candidatos`)
* `GET /candidatos`: Lista todos os candidatos cadastrados.
* `POST /candidatos`: Cadastra um candidato (Exige: `nome`, `email` exclusivo, opcional: `telefone`).
* `GET /candidatos/<id>`: Busca os detalhes de um candidato específico.
* `PUT /candidatos/<id>`: Atualiza dados do candidato (Valida se o novo e-mail já está em uso).
* `DELETE /candidatos/<id>`: Remove o candidato (Contém tratamento caso possua inscrições ativas).

### 📌 Inscrições & RPA (`/inscricoes`)
* `GET /inscricoes`: Lista todas as inscrições efetuadas.
* `POST /inscricoes`: Registra o candidato em uma vaga (Exige: `candidato_id`, `vaga_id`).
  * 🔔 **Trigger RPA:** O serviço dispara, em segundo plano (`threading`), as mensagens automáticas de notificação via WhatsApp (Web) e E-mail sem bloquear a resposta HTTP da API.
* `GET /inscricoes/<id>`: Busca uma inscrição específica pelo ID.
* `PUT /inscricoes/<id>`: Atualiza os dados de uma inscrição (Valida se os novos IDs de vaga ou candidato existem).
* `DELETE /inscricoes/<id>`: Cancela/remove uma inscrição.

### 📌 Assistente Virtual (`/chat`)
* `POST /chat`: Interage com o chatbot de IA.
  * **Payload esperado:** `{"mensagem": "Quais vagas em Home Office estão abertas?"}`
  * **Resposta da API (JSON Estruturado Dinâmico):**
``json
pip install Flask Flask-SQLAlchemy Flask-Cors pywhatkit python-dotenv pyngrok google-genai
```
  * **Como funciona:** O endpoint busca as vagas no banco de dados e as envia junto com a pergunta para o `chatbot.py`. O assistente consome o modelo `gemini-3.1-flash-lite` para responder utilizando estritamente as vagas reais do banco como contexto.

---

## 📝 Observações sobre o WhatsApp Web
A automação gerenciada pelo serviço `rpa.py` abre o WhatsApp Web no navegador padrão do servidor ou máquina local:
* É necessário estar logado previamente na conta do WhatsApp Web no navegador padrão.
* Durante o processamento do `/inscricoes`, o robô abrirá abas do navegador, preencherá o texto e fechará as abas de forma autônoma. Recomenda-se não mover o mouse e teclado durante o ciclo do PyWhatKit para evitar interrupções.
