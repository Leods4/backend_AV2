# 🚀 Projeto Integrador: Portal de Vagas e Automação de Estoque

**Desenvolvedores (Dupla):** [Nome do Dev A] e [Nome do Dev B]

Este repositório contém o código-fonte de dois projetos desenvolvidos em conjunto para a disciplina:
1. **Portal de Vagas:** Uma API RESTful em Flask integrada a um banco SQLite e à inteligência artificial do Gemini, com frontend em HTML/JS e automações de disparo de mensagens.
2. **Sistema de Controle de Estoque:** Um painel interativo em Streamlit com automação de planilhas e rotinas de alertas de estoque.

---

## 🛠️ Tecnologias Utilizadas

**Parte 1: Portal de Vagas**
* **Backend & Banco de Dados:** Python, Flask, Flask-REST, Flask-SQLAlchemy, SQLite
* **Inteligência Artificial:** Google Gemini API (reconhecimento de intenções e respostas abertas)
* **Frontend:** HTML5, Bootstrap, JavaScript (Fetch API)
* **Mensageria (RPA):** PyWhatKit (WhatsApp) e smtplib (E-mail Gmail)

**Parte 2: Sistema de Controle de Estoque**
* **Interface & Backend:** Python, Streamlit, sqlite3
* **Manipulação de Dados:** openpyxl (Excel)
* **Automação & Alertas:** schedule (agendamento) e plyer (notificações no SO)

---

## ⚙️ Pré-requisitos

Antes de executar os projetos, certifique-se de ter instalado em sua máquina:
* [Python 3.8+](https://www.python.org/downloads/)
* Gerenciador de pacotes `pip`
* Uma conta do Google Cloud / Google AI Studio para obter a **Chave de API do Gemini**.
* Um e-mail do Gmail com **Senha de Aplicativo** gerada (para envio de e-mails via código).

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
pip install flask flask-sqlalchemy google-generativeai pywhatkit streamlit openpyxl schedule plyer
```

**4. Configure as Chaves de API e Credenciais:**
* No arquivo `app.py`, localize a variável `genai.configure(api_key="...")` e insira sua chave do Gemini.
* No script de envio de e-mail (RPA), insira seu e-mail do Gmail e a senha de aplicativo gerada para autenticação do SMTP.

---

## 🚀 Como Executar a Aplicação

Este projeto é dividido em frentes diferentes. Siga os passos abaixo para testar cada uma delas:

### 🟢 1. Rodando o Portal de Vagas (Backend e Frontend)

O backend (API) deve estar rodando para que o frontend consiga exibir as vagas, realizar candidaturas e usar o chatbot.

1. No terminal, execute o servidor da API Flask:
   ```bash
   python app.py
   ```
   *O banco de dados `portal_vagas.db` será criado automaticamente na primeira execução e o servidor rodará em `http://127.0.0.1:5000/`.*

2. Com a API rodando, abra o arquivo `index.html` (ou o nome que foi dado à página principal do Portal) no seu navegador web padrão. Você já poderá filtrar vagas e conversar com o chatbot.

3. **Para testar as automações (WhatsApp e E-mail):**
   Execute o script correspondente do Dev B para simular os alertas de aprovação de candidatura.
   ```bash
   python rpa_mensageria.py
   ```

### 🔵 2. Rodando o Sistema de Controle de Estoque

O sistema de estoque utiliza o Streamlit para renderizar a interface no navegador.

1. Abra um novo terminal, ative seu ambiente virtual e navegue até a pasta do estoque.
2. Execute o comando nativo do Streamlit:
   ```bash
   streamlit run app_estoque.py
   ```
3. O painel abrirá automaticamente no seu navegador. Os dados gerados e alterados ficarão salvos na planilha manipulada pelo OpenPyXL e no banco `estoque.db`.

---

## 📄 Notas Adicionais sobre a Apresentação Presencial

* Durante a apresentação, a automação de disparo de e-mail e WhatsApp deverá ser executada **ao vivo**, enviando notificações a um contato real da turma.
* Garanta que o WhatsApp Web da conta emissora esteja devidamente logado caso o script do PyWhatKit exija abertura do navegador.