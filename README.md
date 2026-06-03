# 🚀 Projeto Av2: Portal de Vagas e Automação de Estoque

**Disciplina:** Linguagem de Programação III (Análise e Desenvolvimento de Sistemas)  
**Desenvolvedores (Dupla/Grupo):** [Nome do Dev A] e [Nome do Dev B]

Este repositório contém o código-fonte de dois projetos desenvolvidos em conjunto para a Avaliação Prática 2 (Av2), divididos em duas entregas principais:

1. **Portal de Vagas (Sistema Principal):** Uma API RESTful desenvolvida em Flask, integrada a um banco de dados SQLite e à inteligência artificial do Google Gemini. O projeto conta com frontend interativo, automação (RPA) para envio de mensagens e integração com o **ngrok** para expor a API publicamente de forma segura. O backend possui suporte a CORS aberto para integração nativa com o frontend em qualquer ambiente.
2. **Sistema de Controle de Estoque (Paper RPA):** Um painel interativo em Streamlit com automação de planilhas e rotinas de alertas de estoque, servindo como base para o artigo acadêmico exigido na avaliação.

## 🛠️ Tecnologias Utilizadas

**Parte 1: Portal de Vagas (Projeto Técnico)**
* **Backend & Banco de Dados:** Python, Flask, Flask-SQLAlchemy, Flask-CORS (permitindo requisições cross-origin), SQLite.
* **Exposição de Porta:** Pyngrok (Criação de túnel HTTP para acesso público à API).
* **Inteligência Artificial:** Google Gemini API (reconhecimento de intenções para navegação e respostas via chat).
* **Frontend:** HTML5, CSS3, Bootstrap, JavaScript (Vanilla com Fetch API).
* **Mensageria (RPA):** PyWhatKit (Automação de WhatsApp Web) e smtplib (Envio de e-mails via Gmail).

**Parte 2: Sistema de Controle de Estoque (Paper Acadêmico)**
* **Interface & Banco de Dados Local:** Python, Streamlit, sqlite3.
* **Manipulação de Dados:** openpyxl (Leitura/Escrita de arquivos Excel).
* **Automação & Alertas:** schedule (agendamento de tarefas) e plyer (notificações do sistema operacional).

---

## ⚙️ Pré-requisitos

Antes de executar os projetos, certifique-se de ter instalado em sua máquina:
* Python 3.8+
* Gerenciador de pacotes pip
* Uma chave válida do **Google Gemini API** (via Google AI Studio).
* Uma conta do **Gmail** com uma Senha de Aplicativo gerada (necessária para o script de envio de e-mails não ser bloqueado pelo Google).
* Uma conta gratuita no **ngrok** (para obter o seu `authtoken` e manter a estabilidade do túnel da API).

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
```
* Para ativar no **Windows**: `venv\Scripts\activate`
* Para ativar no **Linux/Mac**: `source venv/bin/activate`

**3. Instale as dependências exigidas no projeto:**
```bash
pip install flask flask-sqlalchemy flask-cors google-generativeai pywhatkit streamlit openpyxl schedule plyer pyngrok
```
*(Nota: `flask-cors` evita bloqueios de segurança do navegador na API, e `pyngrok` conecta seu servidor local à internet).*

**4. Configure as Chaves de API, Ngrok e Credenciais:**
* No terminal, autentique sua conta do ngrok executando: `ngrok config add-authtoken SEU_TOKEN_AQUI`
* No arquivo `app.py`, localize a variável `genai.configure(api_key="SUA_CHAVE_API_AQUI")` e insira sua chave do Gemini.
* No script de RPA (`rpa_mensageria.py`), insira seu endereço do Gmail e a senha de aplicativo gerada nas configurações do SMTP.

---

## 🗺️ Endpoints da API REST (Portal de Vagas)

O backend possui suporte a operações CRUD completas para as 3 entidades do sistema:

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| **GET** | `/vagas` | Lista todas as vagas disponíveis. |
| **POST** | `/vagas` | Cria uma nova vaga. |
| **PUT** | `/vagas/<id>` | Atualiza os dados de uma vaga existente. |
| **DELETE** | `/vagas/<id>` | Remove uma vaga do sistema. |
| **POST** | `/candidatos` | Cadastra um novo candidato (valida e-mail único). |
| **POST** | `/inscricoes` | Relaciona um candidato a uma vaga (candidatura). |
| **POST** | `/chat` | Envia mensagens para o Chatbot (Gemini IA). |

---

## 🚀 Como Executar a Aplicação

Este projeto é dividido em frentes diferentes. Siga os passos abaixo para testar cada uma delas:

### 🟢 1. Rodando o Portal de Vagas (Sistema Principal)

O backend (API) deve estar rodando para que o frontend consiga exibir as vagas, realizar cadastros de candidatos e processar o chatbot.

**Passo A: Iniciar o Servidor Flask e o Túnel Ngrok**
```bash
python app.py
```
> **Nota:** O banco de dados `portal_vagas.db` será criado automaticamente na primeira execução. No seu terminal, uma URL pública gerada pelo ngrok será exibida (ex: `https://xyz.ngrok.app`). **Copie essa URL**, pois ela será a nova base para as requisições do seu frontend.

**Passo B: Acessar a Interface Web**
Certifique-se de que o código JavaScript do seu Frontend está apontando para a URL pública do ngrok gerada no Passo A. Abra o arquivo `index.html` (ou a página principal do Frontend) no seu navegador web padrão. O `CORS` configurado no backend garantirá que tudo funcione perfeitamente.

**Passo C: Testar Automações de RPA (Aprovação/Inscrição)**
Em um novo terminal, execute o script correspondente para disparar os alertas de WhatsApp e E-mail:
```bash
python rpa_mensageria.py
```

### 🔵 2. Rodando o Sistema de Controle de Estoque (Paper)

O sistema secundário utiliza o Streamlit para renderizar o painel interativo.

1. Abra um novo terminal e certifique-se de que o ambiente virtual (`venv`) está ativo.
2. Navegue até o diretório do projeto de estoque.
3. Execute a aplicação com o comando nativo do Streamlit:
```bash
streamlit run app_estoque.py
```
4. O painel abrirá automaticamente no navegador. Os dados manipulados serão atualizados em tempo real na planilha (via `openpyxl`) e no banco local.

---

## 📄 Notas Adicionais para a Apresentação Presencial

* **Público-Alvo:** O sistema deve ser demonstrado com o contexto voltado para os alunos de Processos Gerenciais.
* **Demonstração ao Vivo:** A automação de disparo de e-mail e WhatsApp (`rpa_mensageria.py`) deverá ser executada ao vivo, enviando notificações reais para um integrante da turma-alvo.
* **Importante:** Garanta que o **WhatsApp Web** do navegador padrão utilizado pela máquina de apresentação esteja previamente logado antes de rodar o `PyWhatKit`, para evitar timeout no envio da mensagem. O link do **ngrok** também pode ser compartilhado com os avaliadores para testarem a API em tempo real diretamente de seus dispositivos.
