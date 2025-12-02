from flask import Flask, jsonify, request

app = Flask(__name__)

USERS = [
    {"id": 1, "name": "Jorge", "email": "jorge@example.com", "status": "active"},
    {"id": 2, "name": "Mário", "email": "mario@example.com", "status": "active"},
    {"id": 3, "name": "Carlos", "email": "carlos@example.com", "status": "inactive"},
    {"id": 4, "name": "Maria", "email": "maria@example.com", "status": "active"},
    {"id": 5, "name": "Gustavo", "email": "gustavo@example.com", "status": "active"},
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "users-service"})

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({
        "service": "users-service",
        "total": len(USERS),
        "users": USERS
    })

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in USERS if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "Usuário não encontrado"}), 404

if __name__ == '__main__':
    print("🚀 Users Service rodando na porta 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
