import requests
import time
from datetime import datetime

SERVER_URL = "http://server:8080/status"
INTERVAL = 5

def make_request():
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response = requests.get(SERVER_URL, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[{timestamp}] Requisição bem-sucedida | Servidor: {data.get('hostname')} | Total: {data.get('requests_received')}")
        else:
            print(f"[{timestamp}] Erro: Status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"[{timestamp}] Erro: Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"[{timestamp}] Erro: {str(e)}")

if __name__ == '__main__':
    print(f"Cliente iniciado. Requisições a cada {INTERVAL} segundos para {SERVER_URL}")
    
    while True:
        make_request()
        time.sleep(INTERVAL)