
# 🚀 API Portal de Vagas AV2

Uma API RESTful desenvolvida em Flask para gerenciamento de vagas de emprego, candidatos e inscrições, agora estruturada sob os princípios de **Model-View-Controller (MVC)** para maior escalabilidade e fácil manutenção.

O projeto inclui funcionalidades avançadas, como:
- **Automação RPA:** Disparo de notificações via WhatsApp (PyWhatKit) e E-mail (SMTP) em segundo plano.
- **Inteligência Artificial:** Chatbot integrado ao Google Gemini (via API oficial) para atendimento inteligente aos candidatos.
- **Túnel Público Dinâmico:** Integração nativa com Ngrok para exposição imediata da API local para a internet.

---

## 📁 Estrutura de Diretórios (MVC)

O antigo arquivo monolítico foi substituído por uma arquitetura em pacotes:

```text
portal_vagas_api/
│
├── app/                      # Aplicação Flask (Pacote principal)
│   ├── __init__.py           # Factory Function: Configura o App, BD e CORS
│   ├── models.py             # (Models) Classes do SQLAlchemy (Vaga, Candidato, Inscricao)
│   ├── routes.py             # (Controllers/Views) Definição dos endpoints REST e Blueprints
│   │
│   └── services/             # Lógica de Negócios e Integrações
│       ├── rpa.py            # Orquestração do E-mail e WhatsApp (Logs embutidos)
│       └── chatbot.py        # Configuração do Client e Prompts do Google Gemini
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

> **Primeira execução:** O banco de dados SQLite (`portal_vagas.db`) será criado automaticamente, e uma carga inicial de 3 vagas (Seed) será inserida para facilitar os testes!

---

## 📡 Endpoints Principais (Controllers)

### 📌 Vagas (`/vagas`)
* `GET /vagas`: Lista todas as vagas.
* `POST /vagas`: Cria uma nova vaga (Exige: `titulo`, `descricao`).
* `GET /vagas/<id>`: Busca os detalhes de uma vaga específica.
* `PUT /vagas/<id>`: Atualiza os dados de uma vaga.
* `DELETE /vagas/<id>`: Remove uma vaga.

### 📌 Candidatos (`/candidatos`)
* `POST /candidatos`: Cadastra um candidato (Exige: `nome`, `email`, opcional: `telefone`).

### 📌 Inscrições & RPA (`/inscricoes`)
* `POST /inscricoes`: Registra o candidato em uma vaga (Exige: `candidato_id`, `vaga_id`).
  * 🔔 **Trigger RPA:** O sistema dispara, em segundo plano (`threading`), as mensagens de notificação via WhatsApp (Web) e E-mail.

### 📌 Assistente Virtual (`/chat`)
* `POST /chat`: Interage com o chatbot IA.
  * **Payload esperado:** `{"mensagem": "Tem vaga para programador?"}`
  * **Como funciona:** O `chatbot.py` pega a pergunta, lê o banco de dados em tempo real, injeta o contexto e devolve uma resposta formulada pelo Gemini.

---

## 📝 Observações sobre o WhatsApp Web
A automação `PyWhatKit` abre o WhatsApp Web no navegador padrão da sua máquina. 
* É necessário estar logado previamente no WhatsApp Web.
* Durante a execução do `/inscricoes`, o sistema abrirá abas, digitará a mensagem e as fechará automaticamente. Evite mexer no mouse enquanto o disparo estiver acontecendo.
