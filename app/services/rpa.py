import os
import logging
import smtplib
import pywhatkit
from pathlib import Path
from email.message import EmailMessage

# ====================================================================
# --- SETUP DE LOGS ---
# ====================================================================

# Resolve o diretório raiz do projeto (sube dois níveis: services -> app -> raiz)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(nome_arquivo: str = "automacao.log") -> logging.Logger:
    logger_name = f"rpa_{nome_arquivo}"
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(LOGS_DIR / nome_arquivo, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

email_logger = get_logger("email.log")
whatsapp_logger = get_logger("whatsapp.log")

# ====================================================================
# --- FUNÇÕES DE E-MAIL ---
# ====================================================================

def obter_credenciais() -> tuple[str, str]:
    email_remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")

    if not email_remetente or not senha_app:
        raise ValueError(
            "Defina EMAIL_REMETENTE e EMAIL_SENHA_APP em um arquivo .env."
        )

    return email_remetente, senha_app

def montar_email(destinatario: str, nome: str, vaga: str, empresa: str, link: str | None) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Atualização de candidatura - {vaga}"
    msg["To"] = destinatario

    corpo = (
        f"Olá, {nome},\n\n"
        f"Esta é uma mensagem automática do Portal de Vagas da AV2.\n"
        f"A vaga '{vaga}' na empresa {empresa} está sendo acompanhada pelo sistema.\n"
    )

    if link:
        corpo += f"Link da vaga: {link}\n"

    corpo += "\nMensagem enviada para fins de demonstração da automação com Python.\n"
    msg.set_content(corpo)
    return msg

def enviar_email_smtp(destinatario: str, nome: str, vaga: str, empresa: str, link: str | None) -> None:
    email_remetente, senha_app = obter_credenciais()
    msg = montar_email(destinatario, nome, vaga, empresa, link)
    msg["From"] = email_remetente

    email_logger.info("Iniciando envio de e-mail para %s", destinatario)

    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
        servidor.starttls()
        servidor.login(email_remetente, senha_app)
        servidor.send_message(msg)

    email_logger.info("E-mail enviado com sucesso para %s", destinatario)

# ====================================================================
# --- FUNÇÕES DE WHATSAPP (Pywhatkit) ---
# ====================================================================

def formatar_numero_pywhatkit(numero: str) -> str:
    """Limpa o número e garante que ele tenha o formato +55XXXXXXXXXXX"""
    numero_limpo = numero.strip().replace("+", "").replace("-", "").replace(" ", "")
    
    if not numero_limpo.isdigit():
        raise ValueError("O número de telefone deve conter apenas dígitos após a limpeza.")
    
    # Adiciona o DDI do Brasil (55) se não houver
    if not numero_limpo.startswith("55"):
        numero_limpo = f"55{numero_limpo}"
        
    # Pywhatkit exige o sinal de '+' na frente
    return f"+{numero_limpo}"

def montar_mensagem(nome: str, vaga: str, empresa: str, link: str | None = None) -> str:
    mensagem = (
        f"Olá, {nome}!\n"
        f"A vaga '{vaga}' na empresa {empresa} recebeu uma nova atualização no Portal de Vagas da AV2.\n"
        f"Confira os detalhes e acompanhe a candidatura."
    )
    if link:
        mensagem += f"\nLink: {link}"
    return mensagem

def enviar_whatsapp_pywhatkit(numero_formatado: str, mensagem: str) -> None:
    whatsapp_logger.info("Iniciando envio via Pywhatkit para %s", numero_formatado)
    
    try:
        # wait_time=15: Dá 15 segundos para o WhatsApp Web carregar completamente.
        # tab_close=True e close_time=4: Fecha a aba 4 segundos após o envio para não acumular abas abertas.
        pywhatkit.sendwhatmsg_instantly(
            phone_no=numero_formatado, 
            message=mensagem, 
            wait_time=15, 
            tab_close=True, 
            close_time=4
        )
        whatsapp_logger.info("WhatsApp enviado com sucesso para %s", numero_formatado)
    except Exception as e:
        whatsapp_logger.error(f"Falha ao enviar WhatsApp para {numero_formatado}. Erro: {e}")
        raise

# ====================================================================
# --- ORQUESTRADOR PRINCIPAL ---
# ====================================================================

def executar_automacoes_RPA(email, nome, telefone, titulo_vaga):
    """Executa o envio de e-mail e whatsapp sem bloquear a API."""
    # 1. Tentativa de envio do E-mail
    try:
        enviar_email_smtp(
            destinatario=email,
            nome=nome,
            vaga=titulo_vaga,
            empresa="Portal de Vagas AV2",
            link=None
        )
    except Exception as e:
        email_logger.error(f"[RPA ERRO] Falha no envio de e-mail: {e}")
        print(f"[RPA ERRO] Falha no envio de e-mail: {e}")

    # 2. Tentativa de envio do WhatsApp
    try:
        if telefone and telefone.lower() != 'não informado':
            numero_formatado = formatar_numero_pywhatkit(telefone)

            mensagem = montar_mensagem(
                nome=nome,
                vaga=titulo_vaga,
                empresa="Portal de Vagas AV2",
                link=None
            )
            
            enviar_whatsapp_pywhatkit(numero_formatado=numero_formatado, mensagem=mensagem)
    except Exception as e:
        whatsapp_logger.error(f"[RPA ERRO] Falha no Pywhatkit: {e}")
        print(f"[RPA ERRO] Falha no Pywhatkit: {e}")
