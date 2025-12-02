from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

USERS_SERVICE_URL = os.getenv('USERS_SERVICE_URL', 'http://users-service:5001')
ORDERS_SERVICE_URL = os.getenv('ORDERS_SERVICE_URL', 'http://orders-service:5002')

@app.route('/health', methods=['GET'])
def health():
    """Health check do gateway e serviços downstream"""
    health_status = {"gateway": "ok"}
    
    try:
        users_health = requests.get(f"{USERS_SERVICE_URL}/health", timeout=2)
        health_status["users-service"] = "ok" if users_health.status_code == 200 else "error"
    except:
        health_status["users-service"] = "unreachable"
    
    try:
        orders_health = requests.get(f"{ORDERS_SERVICE_URL}/health", timeout=2)
        health_status["orders-service"] = "ok" if orders_health.status_code == 200 else "error"
    except:
        health_status["orders-service"] = "unreachable"
    
    return jsonify(health_status)

@app.route('/users', methods=['GET'])
def get_users():
    """Roteia para users-service"""
    try:
        response = requests.get(f"{USERS_SERVICE_URL}/users", timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Users service indisponível", "details": str(e)}), 503

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Roteia para users-service com ID específico"""
    try:
        response = requests.get(f"{USERS_SERVICE_URL}/users/{user_id}", timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Users service indisponível", "details": str(e)}), 503

@app.route('/orders', methods=['GET'])
def get_orders():
    """Roteia para orders-service"""
    user_id = request.args.get('user_id')
    
    try:
        url = f"{ORDERS_SERVICE_URL}/orders"
        if user_id:
            url += f"?user_id={user_id}"
        
        response = requests.get(url, timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Orders service indisponível", "details": str(e)}), 503

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Roteia para orders-service com ID específico"""
    try:
        response = requests.get(f"{ORDERS_SERVICE_URL}/orders/{order_id}", timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Orders service indisponível", "details": str(e)}), 503

@app.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_with_orders(user_id):
    """Agrega dados de usuário + pedidos em uma única chamada"""
    try:
        user_response = requests.get(f"{USERS_SERVICE_URL}/users/{user_id}", timeout=5)
        if user_response.status_code == 404:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        user_data = user_response.json()
        
        orders_response = requests.get(f"{ORDERS_SERVICE_URL}/orders?user_id={user_id}", timeout=5)
        orders_data = orders_response.json()
        
        result = {
            "user": user_data,
            "orders": orders_data.get("orders", []),
            "total_orders": orders_data.get("total", 0)
        }
        
        return jsonify(result)
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Erro ao agregar dados", "details": str(e)}), 503

if __name__ == '__main__':
    print("API Gateway rodando na porta 8080")
    print(f"Users Service: {USERS_SERVICE_URL}")
    print(f"Orders Service: {ORDERS_SERVICE_URL}")
    app.run(host='0.0.0.0', port=8080, debug=False)