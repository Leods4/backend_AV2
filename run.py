# run.py (Na raiz do projeto)
import os
from pyngrok import ngrok
from dotenv import load_dotenv
from app import create_app

# 1. Carrega as variáveis de ambiente (antes de criar o app)
load_dotenv()

# 2. Cria a instância da aplicação através da Factory Function
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    
    ngrok_token = os.getenv('NGROK_AUTH_TOKEN')
    ngrok_domain = os.getenv('NGROK_DOMAIN')
    
    if ngrok_token:
        ngrok.set_auth_token(ngrok_token)
    
    if ngrok_domain:
        public_url = ngrok.connect(port, domain=ngrok_domain).public_url
    else:
        public_url = ngrok.connect(port).public_url
        
    print(f"\n * Túnel Ngrok ativo! Acesse sua API por aqui: {public_url}\n")
    
    # Inicia o servidor Flask
    app.run(debug=True, port=port, use_reloader=False)