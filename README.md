# 🚀 Projeto Av2: Portal de Vagas e Automação de Estoque

**Disciplina:** Linguagem de Programação III (Análise e Desenvolvimento de Sistemas)  
**Desenvolvedores (Dupla/Grupo):** [Nome do Dev A] e [Nome do Dev B]  

Este repositório contém o código-fonte de dois projetos desenvolvidos em conjunto para a Avaliação Prática 2 (Av2), divididos em duas entregas principais:

* **Portal de Vagas (Sistema Principal):** Uma API RESTful desenvolvida em Flask, integrada a um banco de dados SQLite e à inteligência artificial do Google Gemini. O projeto conta com frontend interativo, automação (RPA) para envio de mensagens e integração com o ngrok para expor a API publicamente de forma segura. O backend possui suporte a CORS aberto para integração nativa com o frontend em qualquer ambiente.
* **Sistema de Controle de Estoque (Paper RPA):** Um painel interativo em Streamlit com automação de planilhas e rotinas de alertas de estoque, servindo como base para o artigo acadêmico exigido na avaliação.

---

## 🛠️ Tecnologias Utilizadas

**Parte 1: Portal de Vagas (Projeto Técnico)**
* **Backend & Banco de Dados:** Python, Flask, Flask-SQLAlchemy, Flask-CORS (permitindo requisições cross-origin), python-dotenv, SQLite.
* **Exposição de Porta:** Pyngrok (Criação de túnel HTTP para acesso público à API com domínio fixo ou dinâmico).
* **Inteligência Artificial:** Google Gemini API (reconhecimento de intenções para navegação e respostas via chat).
* **Frontend:** HTML5, CSS3, Bootstrap, JavaScript (Vanilla com Fetch API).
* **Mensageria e Automação (RPA):** PyWhatKit (WhatsApp Web), smtplib (E-mails via Gmail) e biblioteca nativa `threading` (para execução em segundo plano sem travar a API).

**Parte 2: Sistema de Controle de Estoque (Paper Acadêmico)**
* **Interface & Banco de Dados Local:** Python, Streamlit, sqlite3.
* **Manipulação de Dados:** openpyxl (Leitura/Escrita de arquivos Excel).
* **Automação & Alertas:** schedule (agendamento de tarefas) e plyer (notificações do sistema operacional).

---

## ⚙️ Pré-requisitos

Antes de executar os projetos, certifique-se de ter instalado em sua máquina:
* **Python 3.8+** e gerenciador de pacotes **pip**.
* Uma chave válida do **Google Gemini API** (via Google AI Studio).
* Uma conta do **Gmail** com uma *Senha de Aplicativo* gerada (necessária para o envio de e-mails não ser bloqueado pelo Google).
* Uma conta gratuita no **ngrok** (para obter o seu authtoken e manter a estabilidade do túnel da API).

---

## 📦 Instalação e Configuração

**1. Clone este repositório:**
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
```

**2. Crie e ative um ambiente virtual (Recomendado):**
```bash
python -m venv venv

# Para ativar no Windows: 
venv\Scripts\activate
# Para ativar no Linux/Mac: 
source venv/bin/activate
```

**3. Instale as dependências exigidas no projeto:**
```bash
pip install flask flask-sqlalchemy flask-cors google-generativeai pywhatkit streamlit openpyxl schedule plyer pyngrok python-dotenv
```

**4. Configuração das Variáveis de Ambiente (.env):**
Para manter suas chaves e senhas seguras, crie um arquivo chamado exatamente **`.env`** na raiz do projeto (na mesma pasta de `app.py`) e adicione as suas configurações seguindo este modelo:

```env
# Configurações do Servidor
FLASK_ENV=development
FLASK_PORT=5000
DATABASE_URL=sqlite:///portal_vagas.db

# Credenciais e Chaves de API
GEMINI_API_KEY=sua_chave_do_gemini_aqui

# Configurações do Ngrok
NGROK_AUTH_TOKEN=seu_token_do_ngrok_aqui
NGROK_DOMAIN=seu-dominio-estatico.ngrok-free.dev # Opcional (apague a linha se não tiver)

# Credenciais de Automação de E-mail (RPA)
EMAIL_REMETENTE=seu-email@gmail.com
EMAIL_SENHA_APP=sua_senha_de_aplicativo_de_16_digitos_aqui
```

---

## 🗺️ Endpoints da API REST (Portal de Vagas)

O backend possui suporte a operações CRUD completas para as entidades do sistema:

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| **GET** | `/` | Rota raiz de conexão (Health Check) para o botão "Testar conexão" do frontend. |
| **GET** | `/vagas` | Lista todas as vagas disponíveis. |
| **GET** | `/vagas/<id>` | Busca os dados de uma vaga específica pelo seu ID. |
| **POST** | `/vagas` | Cria uma nova vaga. |
| **PUT** | `/vagas/<id>` | Atualiza os dados de uma vaga existente. |
| **DELETE** | `/vagas/<id>` | Remove uma vaga do sistema. |
| **POST** | `/candidatos` | Cadastra um novo candidato (valida e-mail único). |
| **POST** | `/inscricoes` | Relaciona candidato a uma vaga e **dispara o RPA (E-mail e WhatsApp)**. |
| **POST** | `/chat` | Envia mensagens para o Chatbot (Gemini IA). |

---

## 🚀 Como Executar a Aplicação

Este projeto é dividido em frentes diferentes. Siga os passos abaixo para testar cada uma delas:

### 🟢 1. Rodando o Portal de Vagas (Sistema Principal)

O backend (API) deve estar rodando para que o frontend consiga exibir as vagas, realizar cadastros de candidatos e processar o chatbot.

* **Passo A: Iniciar o Servidor Flask e o Túnel Ngrok**
    ```bash
    python app.py
    ```
    *Nota:* O banco de dados `portal_vagas.db` será criado automaticamente e populado com dados de teste na primeira execução. No terminal, a URL pública gerada pelo ngrok será exibida.

* **Passo B: Configurar e Acessar o Frontend**
    Copie a URL do ngrok gerada no terminal e atualize a variável `API_BASE_URL` no seu arquivo `config.js` do frontend. Em seguida, abra o arquivo `index.html` no seu navegador web padrão. O cabeçalho especial no `api.js` contornará a tela de aviso do ngrok.

* **Passo C: Testar as Automações (RPA Integrado)**
    Você **não** precisa mais rodar scripts de automação manualmente no terminal. No frontend, cadastre um candidato e clique em **"Candidatar"** em qualquer vaga. O backend criará uma *Thread* em segundo plano que enviará o E-mail e abrirá o WhatsApp Web automaticamente no navegador do servidor, sem travar a experiência do usuário no frontend!

### 🔵 2. Rodando o Sistema de Controle de Estoque (Paper)

O sistema secundário utiliza o Streamlit para renderizar o painel interativo.
1.  Abra um novo terminal e certifique-se de que o ambiente virtual (`venv`) está ativo.
2.  Navegue até o diretório do projeto de estoque.
3.  Execute a aplicação com o comando nativo do Streamlit:
    ```bash
    streamlit run app_estoque.py
    ```
4.  O painel abrirá automaticamente no navegador. Os dados manipulados serão atualizados em tempo real na planilha (via `openpyxl`) e no banco local.

---

## 📄 Notas Adicionais para a Apresentação Presencial

* **Público-Alvo:** O sistema deve ser demonstrado com o contexto voltado para os alunos de Processos Gerenciais.
* **Demonstração ao Vivo do RPA:** A automação de disparo de e-mail e WhatsApp foi integrada à rota de candidaturas. Ao demonstrar, simule uma candidatura real para um integrante da turma-alvo usando o frontend.
* **Importante para o WhatsApp:** Garanta que o WhatsApp Web do navegador padrão utilizado pela máquina da apresentação esteja **previamente logado e com a sessão ativa** antes de clicar em "Candidatar" no frontend. Isso evita falhas de *timeout* do `PyWhatKit` ao tentar carregar a aba.
* **Acessibilidade:** O link do ngrok pode ser compartilhado com os avaliadores para que eles testem o frontend e o consumo da API em tempo real diretamente dos próprios smartphones ou notebooks.
