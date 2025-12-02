from flask import Flask, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

SERVICE_A_URL = os.getenv('SERVICE_A_URL', 'http://service-a:5001')

def calculate_days_since(date_str):
    """Calcula quantos dias desde a data fornecida"""
    created = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.now()
    delta = today - created
    return delta.days

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "report-service"})

@app.route('/report', methods=['GET'])
def get_report():
    """Consome service-a e gera relatório formatado"""
    try:
        response = requests.get(f"{SERVICE_A_URL}/users", timeout=5)
        
        if response.status_code != 200:
            return jsonify({"error": "Erro ao buscar usuários"}), 500
        
        data = response.json()
        users = data.get('users', [])
        
        # Gera relatório combinado
        report = []
        for user in users:
            days_active = calculate_days_since(user['created_at'])
            
            report.append({
                "user_id": user['id'],
                "message": f"Usuário {user['name']} ativo desde {user['created_at']} ({days_active} dias)",
                "email": user['email'],
                "days_active": days_active
            })
        
        return jsonify({
            "service": "report-service",
            "generated_at": datetime.now().isoformat(),
            "total_users": len(report),
            "report": report
        })
    
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Não foi possível conectar ao Users Service"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report/<int:user_id>', methods=['GET'])
def get_user_report(user_id):
    """Gera relatório de um usuário específico"""
    try:
        response = requests.get(f"{SERVICE_A_URL}/users/{user_id}", timeout=5)
        
        if response.status_code == 404:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        if response.status_code != 200:
            return jsonify({"error": "Erro ao buscar usuário"}), 500
        
        user = response.json()
        days_active = calculate_days_since(user['created_at'])
        
        return jsonify({
            "user_id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "registered_on": user['created_at'],
            "days_active": days_active,
            "status": f"Usuário {user['name']} ativo desde {user['created_at']} ({days_active} dias)"
        })
    
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Não foi possível conectar ao Users Service"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Report Service iniciado na porta 5002")
    print(f"Conectando ao Users Service em: {SERVICE_A_URL}")
    app.run(host='0.0.0.0', port=5002, debug=False)