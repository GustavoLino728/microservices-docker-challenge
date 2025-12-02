from flask import Flask, jsonify
from datetime import datetime, timedelta
import random

app = Flask(__name__)

USERS = [
    {"id": 1, "name": "Jorge", "email": "jorge@example.com", "created_at": "2024-01-15"},
    {"id": 2, "name": "Mário", "email": "mario@example.com", "created_at": "2024-03-22"},
    {"id": 3, "name": "Carlos", "email": "carlos@example.com", "created_at": "2024-06-10"},
    {"id": 4, "name": "Maria", "email": "maria@example.com", "created_at": "2024-08-05"},
    {"id": 5, "name": "Gustavo Lino", "email": "gustavo@example.com", "created_at": "2024-11-20"},
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "users-service"})

@app.route('/users', methods=['GET'])
def get_users():
    """Retorna lista completa de usuários"""
    return jsonify({
        "service": "users-service",
        "total": len(USERS),
        "users": USERS
    })

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retorna um usuário específico"""
    user = next((u for u in USERS if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "Usuário não encontrado"}), 404

if __name__ == '__main__':
    print("Users Service iniciado na porta 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)