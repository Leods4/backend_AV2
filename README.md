# Portal de Vagas AV2 — API RESTful, Chatbot com IA e Automação RPA

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.x-green.svg)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-ORM-red.svg)
![Gemini](https://img.shields.io/badge/Google%20Gemini-3.1%20Flash%20Lite-orange.svg)
![Ngrok](https://img.shields.io/badge/ngrok-Tunnel-darkviolet.svg)

Bem-vindo ao repositório do **Portal de Vagas AV2**, uma solução de backend corporativa desenvolvida em Python com o ecossistema Flask. Este sistema consolida uma arquitetura baseada em serviços para gerenciamento de processos seletivos (CRUD completo de vagas, candidatos e inscrições), potencializada por um **Chatbot Recrutador com Inteligência Artificial** (Google Gemini) e um **Motor de Automação RPA** assíncrono para notificações via E-mail (SMTP) e WhatsApp.

---

## 📌 Índice
1. [Arquitetura do Projeto e Estrutura de Pastas](#-arquitetura-do-projeto-e-estrutura-de-pastas)
2. [Modelagem do Banco de Dados (Camada de Persistência)](#-modelagem-do-banco-de-dados-camada-de-persistência)
3. [Instalação e Configuração do Ambiente](#-instalação-e-configuração-do-ambiente)
4. [Variáveis de Ambiente (.env)](#-variáveis-de-ambiente-env)
5. [Execução e Exposição Global (Ngrok)](#-execução-e-exposição-global-ngrok)
6. [Documentação Completa da API (Endpoints)](#-documentação-completa-da-api-endpoints)
7. [Arquitetura do Chatbot IA e Guardrails](#-arquitetura-do-chatbot-ia-e-guardrails)
8. [Funcionamento do Orquestrador RPA Assíncrono](#-funcionamento-do-orquestrador-rpa-assíncrono)
9. [Tratamento de Erros e Logs](#-tratamento-de-erros-e-logs)

---

## 📂 Arquitetura do Projeto e Estrutura de Pastas

O sistema adota o padrão de design **Service-Layer Architecture** acoplado ao conceito de **Application Factory** do Flask, isolando completamente as rotas (controladores), as regras de negócio (serviços) e as entidades de dados (modelos).

```text
portal-vagas-av2/
│
├── app/
│   ├── __init__.py              # Configuração da Application Factory e Inicialização do DB
│   ├── models.py                # Definição das Tabelas e Relacionamentos do SQLAlchemy
│   ├── routes.py                # Centralização dos Endpoints da API via Flask Blueprints
│   │
│   └── services/
│       ├── __init__.py          # Inicializador do pacote de serviços
│       ├── candidato_service.py # Lógica de Negócio e Validações de Candidatos
│       ├── vaga_service.py      # Lógica de Negócio e Validações de Vagas
│       ├── inscricao_service.py # Lógica de Inscrições e Despacho de Threads do RPA
│       ├── chatbot.py           # Integração Nativa com Google GenAI SDK (Gemini)
│       └── rpa.py               # Motores de Notificação (SMTP Mail e Pywhatkit)
│
├── logs/                        # Diretório Autogerado de Auditoria do RPA
│   ├── email.log                # Histórico de Envios e Falhas de E-mail
│   └── whatsapp.log             # Histórico de Interações do Pywhatkit
│
├── .env                         # Arquivo Protegido de Variáveis de Ambiente
├── run.py                       # Ponto de Entrada da Aplicação e Configuração do Túnel Ngrok
└── requirements.txt             # Manifesto de Dependências do Projeto
```

---

## 🗄️ Modelagem do Banco de Dados (Camada de Persistência)

A persistência de dados é estruturada sobre um banco de dados relacional gerenciado através do SQLAlchemy ORM. O esquema é composto por três entidades principais com integridade referencial estrita:

### 1. Entidade: `Candidato` (`__tablename__ = 'candidato'`)
* `id` (Integer, Primary Key): Identificador único sequencial.
* `nome` (String(100), Nullable=False): Nome completo do candidato.
* `email` (String(100), Unique=True, Nullable=False): E-mail único de identificação corporativa.
* `telefone` (String(20), Nullable=True): Número telefónico (padrão: "Não informado").
* *Relacionamento*: `inscricoes` (backref='candidato', lazy=True) -> Relacionamento 1:N com a tabela `Inscricao`.

### 2. Entidade: `Vaga` (`__tablename__ = 'vaga'`)
* `id` (Integer, Primary Key): Identificador único da vaga.
* `titulo` (String(100), Nullable=False): Título do cargo/oportunidade.
* `descricao` (Text, Nullable=False): Detalhamento dos requisitos e atividades.
* `area` (String(50), Nullable=False): Departamento/Área de Atuação.
* `modalidade` (String(50), Nullable=False): Regime de trabalho (Ex: Presencial, Híbrido, Remoto).
* *Relacionamento*: `inscricoes` (backref='vaga', lazy=True) -> Relacionamento 1:N com a tabela `Inscricao`.

### 3. Entidade: `Inscricao` (`__tablename__ = 'inscricao'`)
* `id` (Integer, Primary Key): Identificador único do registro de candidatura.
* `data_inscricao` (DateTime): Carimbo de data/hora UTC gerado automaticamente no ato do cadastro.
* `candidato_id` (Integer, ForeignKey('candidato.id'), Nullable=False): Chave Estrangeira vinculada ao Candidato.
* `vaga_id` (Integer, ForeignKey('vaga.id'), Nullable=False): Chave Estrangeira vinculada à Vaga.

---

## 📥 Instalação e Configuração do Ambiente

Siga as diretrizes abaixo para clonar, isolar o ambiente e instalar o ecossistema de dependências da aplicação.

1. **Clonagem do Repositório:**
   ```bash
   git clone [https://github.com/seu-usuario/portal-vagas-av2.git](https://github.com/seu-usuario/portal-vagas-av2.git)
   cd portal-vagas-av2
   ```

2. **Isolamento de Ambiente Virtual (Virtualenv):**
   ```bash
   # Criação do ambiente virtual utilizando a versão do Python instalada
   python -m venv venv

   # Ativação do ambiente - Sistemas Windows (Prompt/PowerShell)
   .\venv\Scripts\activate

   # Ativação do ambiente - Sistemas Unix (Linux/macOS)
   source venv/bin/activate
   ```

3. **Instalação dos Pacotes Requeridos:**
   ```bash
   pip install --upgrade pip
   pip install flask flask-sqlalchemy python-dotenv pyngrok google-genai pywhatkit
   ```

---

## ⚙️ Variáveis de Ambiente (.env)

Crie um arquivo `.env` localizado obrigatoriamente na raiz do projeto. Este arquivo armazena chaves privadas de API, credenciais de servidores SMTP e definições de infraestrutura.

```ini
# Configurações do Servidor Web Flask
FLASK_PORT=5000

# Infraestrutura de Redes e Túnel Ngrok
# Obtenha o token gratuitamente em dashboard.ngrok.com
NGROK_AUTH_TOKEN=seu_token_autenticacao_ngrok_aqui
# Opcional: configure caso tenha um domínio estático configurado no painel do Ngrok
NGROK_DOMAIN=seu_dominio_estatico_opcional.ngrok-free.app

# Provedor de Inteligência Artificial Generativa
# Crie sua chave em console.alphavantage.co / aistudio.google.com
GEMINI_API_KEY=AIzaSyA_SuaChavePrivadaDoGeminiAqui

# Credenciais do Orquestrador RPA de Notificações
# Recomendado utilizar o Gmail com uma 'Senha de App' gerada nas configurações de segurança do Google Account
EMAIL_REMETENTE=seu_email_corporativo_ou_pessoal@gmail.com
EMAIL_SENHA_APP=abcd efgh ijkl mnop
```

---

## 🏃 Execução e Exposição Global (Ngrok)

Para iniciar o ecossistema completo de backend integrado à exposição automática via túnel seguro na internet, execute:

```bash
python run.py
```

### Comportamento do Lifecycle de Inicialização:
1. O pacote `python-dotenv` faz o parse de todas as credenciais do `.env`.
2. O script detecta a presença de `NGROK_AUTH_TOKEN`, autentica o cliente local e inicializa um túnel proxy reverso mapeando a porta local (`FLASK_PORT`) para um subdomínio público criptografado em HTTPS.
3. A URL gerada pelo Ngrok (Ex: `https://seu-subdominio.ngrok-free.app`) é impressa no terminal. Esta URL deve ser inserida nas configurações do seu cliente frontend.
4. O servidor Flask entra em modo de escuta com o recarregador desativado (`use_reloader=False`) para garantir a estabilidade da execução paralela de threads do Pywhatkit e do Ngrok.

---

## 📡 Documentação Completa da API (Endpoints)

### 🩺 Rota de Monitorização (Health Check)
* **`GET /`**
  * **Objetivo**: Validar a conectividade externa e o status operacional da API (usado pelo botão 'Testar Conexão' do painel administrativo).
  * **Código de Sucesso**: `200 OK`
  * **Response Payload (JSON)**:
    ```json
    {
      "status": "Online",
      "mensagem": "Conexão com a API realizada com sucesso!"
    }
    ```

---

### 💼 Módulo de Vagas de Emprego
* **`GET /vagas`**
  * **Objetivo**: Recuperar a listagem integral de todas as vagas registradas no banco.
  * **Código de Sucesso**: `200 OK`
  * **Response Payload**:
    ```json
    [
      {
        "id": 1,
        "titulo": "Desenvolvedor Python Full Stack Senior",
        "descricao": "Atuar no desenvolvimento de APIs robustas usando Flask e integrações de IA.",
        "area": "Tecnologia da Informação",
        "modalidade": "Remoto"
      }
    ]
    ```

* **`POST /vagas`**
  * **Objetivo**: Criar uma nova oportunidade de emprego.
  * **Request Payload (Obrigatório)**:
    ```json
    {
      "titulo": "Analista de Dados Pleno",
      "descricao": "Manipulação de dados volumosos com Pandas e construção de dashboards.",
      "area": "Business Intelligence",
      "modalidade": "Híbrido"
    }
    ```
  * **Códigos de Resposta**:
    * `201 Created`: Sucesso na inserção. Retorna `{"mensagem": "Vaga criada com sucesso!", "id": 2}`.
    * `400 Bad Request`: Dados ausentes ou incompletos. Retorna `{"erro": "Dados incompletos. Titulo e descricao são obrigatórios."}`.

* **`GET /vagas/<int:id>`**
  * **Códigos de Resposta**: `200 OK` com os dados estruturados da vaga, ou `404 Not Found` -> `{"erro": "Vaga não encontrada"}`.

* **`PUT /vagas/<int:id>`**
  * **Objetivo**: Atualização parcial/total de atributos da vaga via patch de dados. Retorna `200 OK` com mensagem de sucesso caso localizada, ou `404 Not Found`.

* **`DELETE /vagas/<int:id>`**
  * **Objetivo**: Exclusão física da vaga da base de dados. Retorna `200 OK`.

---

### 👥 Módulo de Candidatos
* **`GET /candidatos`** e **`GET /candidatos/<id>`** -> Listagem estruturada de perfis.
* **`POST /candidatos`**
  * **Request Payload**:
    ```json
    {
      "nome": "Carlos Silva",
      "email": "carlos.silva@email.com",
      "telefone": "+5511999998888"
    }
    ```
  * **Códigos de Resposta**:
    * `201 Created`: Sucesso. Retorna mensagem e o `id` gerado.
    * `400 Bad Request`: Nome ou E-mail ausente, ou duplicação de e-mail na base (`{"erro": "Este e-mail já está cadastrado."}`).

* **`PUT /candidatos/<int:id>`** -> Atualiza os atributos. Valida de forma estrita a unicidade de e-mail se houver alteração (`{"erro": "Este e-mail já está cadastrado por outro usuário."}`).
* **`DELETE /candidatos/<int:id>`**
  * **Comportamento Crítico**: Se o candidato possuir registros vinculados na tabela de `Inscricao`, o banco levanta uma restrição de integridade (Foreign Key Constraint Fail). O serviço captura a exceção, realiza o `db.session.rollback()` e devolve um código `400 Bad Request` informando o impedimento comercial.

---

### 📝 Módulo de Inscrições e Candidaturas
* **`POST /inscricoes`**
  * **Objetivo**: Realizar o vínculo de candidatura entre um candidato existente e uma vaga ativa. **Este endpoint dispara o fluxo assíncrono de RPA em Background.**
  * **Request Payload**:
    ```json
    {
      "candidato_id": 1,
      "vaga_id": 1
    }
    ```
  * **Códigos de Resposta**:
    * `201 Created`: Inscrição efetuada com sucesso. Inicia imediatamente as notificações em segundo plano.
      ```json
      {
        "id": 5,
        "mensagem": "Inscrição realizada com sucesso! Notificações automáticas em processamento."
      }
      ```
    * `404 Not Found`: Candidato ou Vaga inexistente na base (`{"erro": "Candidato não encontrado."}` ou `{"erro": "Vaga não encontrada."}`).

---

### 🤖 Módulo do Chatbot Inteligente com IA
* **`POST /chat`**
  * **Objetivo**: Canal de conversação em linguagem natural estruturado para interfaces web/mobile.
  * **Request Payload**:
    ```json
    {
      "mensagem": "Olá, gostaria de saber se vocês têm vagas para trabalhar em home office na área de TI?"
    }
    ```
  * **Fluxo Operacional**: O serviço puxa todas as vagas ativas no banco de dados SQLite, injeta-as dentro de um contexto estruturado de prompts (*Guardrails*) e submete ao modelo `gemini-3.1-flash-lite`.
  * **Códigos de Resposta**:
    * `200 OK`: Interação bem-sucedida. O chatbot responde estritamente no formato classificado.
      ```json
      {
        "intencao": "consulta_vagas",
        "resposta": "Olá! Temos sim. Atualmente possuímos a vaga de Desenvolvedor Python Full Stack Senior na área de Tecnologia da Informação que é 100% Remota."
      }
      ```
    * `500 Internal Server Error`: Falhas críticas na comunicação com os servidores do Google GenAI Studio.

---

## 🧠 Arquitetura do Chatbot IA e Guardrails

O motor do chatbot contido em `chatbot.py` utiliza o modelo `gemini-3.1-flash-lite`. Para garantir respostas corporativas previsíveis e evitar alucinações comuns em LLMs, o sistema adota regras severas de contexto e engenharia de prompt:

1. **Injeção Dinâmica de Contexto (Zero-Shot RAG)**: O banco de dados consulta todas as vagas reais do sistema e reconstrói uma string contendo título, área, modalidade e descrição. O modelo só conhece e pode responder sobre estas vagas informadas.
2. **Guardrails de Comportamento**:
   * O robô está instruído a recusar educadamente qualquer assunto que fuja de carreiras ou suporte do Portal da AV2.
   * É estritamente proibido criar, assumir ou inventar vagas que não estejam presentes na lista contextualizada.
3. **Casamento Forçado de Tipo (JSON Schema Enforcement)**:
   * O prompt força o modelo a responder **exclusivamente** com um payload JSON válido com duas chaves estruturais: `"resposta"` e `"intencao"`.
   * A IA atua também como um classificador NLU em tempo real, rotulando dinamicamente a mensagem do usuário em uma das seguintes intenções:
     * `consulta_vagas`: Usuário procurando por oportunidades.
     * `candidatura`: Intenção clara de inscrição ou envio de currículo.
     * `atendimento_bot`: Interações gerais, saudações, interjeições ou despedidas.
4. **Resiliência a Falhas de Parse**: O código envolve a chamada em um bloco de tratamento de exceções para capturar `json.JSONDecodeError`. Se a IA falhar na formatação estrutural do JSON bruto, um mecanismo de *fallback* automático captura o texto puro e padroniza a intenção como `atendimento_bot`.

---

## ⚙️ Funcionamento do Orquestrador RPA Assíncrono

Para manter a experiência do usuário fluida e a API ágil, o envio de notificações não ocorre de maneira linear. O arquivo `inscricao_service.py` despacha o processamento robótico para um thread independente baseado no módulo nativo `threading.Thread`.

```text
[Cliente] -> HTTP POST /inscricoes -> [API Flask]
                                         │
                                         ├──> Grava no Banco SQLite e retorna HTTP 201 imediatamente.
                                         │
                                         └──> [Despacha Thread RPA Independente]
                                                   │
                                                   ├──> Executa enviar_email_smtp()
                                                   └──> Executa enviar_whatsapp_pywhatkit()
```

### Detalhes das Rotinas do Robô (`rpa.py`):

1. **Motor de E-mail (SMTP)**:
   * Conecta-se ao host criptografado `smtp.gmail.com` através da porta TLS `587`.
   * Monta uma estrutura MIME utilizando a biblioteca padrão `email.message.EmailMessage`, prevenindo injeções de cabeçalho indesejadas e padronizando a codificação de caracteres em UTF-8.

2. **Motor de WhatsApp (Pywhatkit)**:
   * **Higienização de Entradas**: O método `formatar_numero_pywhatkit` limpa strings removendo espaços, caracteres especiais, hifens e o símbolo `+`. Adiciona o código de discagem internacional (DDI) brasileiro `55` caso o input não possua e prefixa o caracter `+` exigido pela biblioteca.
   * **Simulação de Interface Humana**: O método `pywhatkit.sendwhatmsg_instantly` assume o controle do sistema de janelas do SO para abrir o navegador padrão no WhatsApp Web. O parâmetro `wait_time=15` garante um delay seguro de 15 segundos para o carregamento completo do DOM da página antes de disparar o gatilho de envio. Os parâmetros `tab_close=True` e `close_time=4` fecham a aba automaticamente 4 segundos após a conclusão do disparo do texto, impedindo o vazamento de memória e o acúmulo desordenado de abas abertas no servidor.

---

## 📝 Tratamento de Erros e Logs

A automação RPA é totalmente isolada para que falhas externas (como falta de internet, chaves incorretas ou token SMTP inválido) nunca quebrem a transação de banco de dados da inscrição.

* **Diretório de Logs**: No momento da primeira execução, a aplicação localiza o diretório raiz do projeto e cria de forma programática a pasta `/logs`.
* **Segregação de Loggers**: Foram criados dois pipelines independentes através da biblioteca padrão `logging`:
  * `email.log`: Registra timestamps, níveis de severidade (INFO, ERROR) e mensagens de rastreabilidade de entrega de e-mails.
  * `whatsapp.log`: Registra o ciclo completo de acionamento e as falhas operacionais encontradas no controle do Pywhatkit.
* **Captura de Exceções Criticas**: Toda falha é capturada, gravada nos arquivos de log com o traceback simplificado e exibida via console (`print`), permitindo depuração ágil sem interrupção de microsserviços paralelos.
