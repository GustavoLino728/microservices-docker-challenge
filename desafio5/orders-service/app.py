from flask import Flask, jsonify, request

app = Flask(__name__)

ORDERS = [
    {"id": 101, "user_id": 1, "product": "Notebook Dell", "amount": 3500.00, "status": "delivered"},
    {"id": 102, "user_id": 1, "product": "Mouse Logitech", "amount": 150.00, "status": "delivered"},
    {"id": 103, "user_id": 2, "product": "Teclado Mecânico", "amount": 450.00, "status": "pending"},
    {"id": 104, "user_id": 4, "product": "Monitor LG 27\"", "amount": 1200.00, "status": "shipped"},
    {"id": 105, "user_id": 5, "product": "Headset Gamer", "amount": 320.00, "status": "delivered"},
    {"id": 106, "user_id": 5, "product": "Webcam HD", "amount": 280.00, "status": "pending"},
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "orders-service"})

@app.route('/orders', methods=['GET'])
def get_orders():
    user_id = request.args.get('user_id', type=int)
    
    if user_id:
        filtered = [o for o in ORDERS if o["user_id"] == user_id]
        return jsonify({
            "service": "orders-service",
            "user_id": user_id,
            "total": len(filtered),
            "orders": filtered
        })
    
    return jsonify({
        "service": "orders-service",
        "total": len(ORDERS),
        "orders": ORDERS
    })

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({"error": "Pedido não encontrado"}), 404

if __name__ == '__main__':
    print("🚀 Orders Service rodando na porta 5002")
    app.run(host='0.0.0.0', port=5002, debug=False)