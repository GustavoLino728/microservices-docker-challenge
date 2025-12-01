from flask import Flask, request, jsonify
from models import User, get_session, init_db
import redis
import os
import json
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

@app.route('/init-db', methods=['GET'])
def startup():
    init_db()
    return jsonify({"status": "db_initialized"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "redis": redis_client.ping()})

@app.route('/users', methods=['GET'])
def list_users():
    cache_key = "users_list"
    cached = redis_client.get(cache_key)
    
    if cached:
        return jsonify(json.loads(cached))
    
    session = get_session()
    users = session.query(User).all()
    users_json = [{"id": u.id, "name": u.name, "email": u.email} for u in users]
    
    redis_client.set(cache_key, json.dumps(users_json), ex=60)
    session.close()
    return jsonify(users_json)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    session = get_session()
    user = User(name=data['name'], email=data['email'])
    
    try:
        session.add(user)
        session.commit()
        session.refresh(user)        
        redis_client.delete("users_list")
        
        return jsonify({"id": user.id, "name": user.name, "email": user.email}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Email já existe"}), 400
    finally:
        session.close()

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    cache_key = f"user_{user_id}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return jsonify(json.loads(cached))
    
    session = get_session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    
    if user:
        data = {"id": user.id, "name": user.name, "email": user.email}
        redis_client.set(cache_key, json.dumps(data), ex=300)
        return jsonify(data)
    return jsonify({"error": "Usuário não encontrado"}), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    
    session = get_session()
    user = session.query(User).filter(User.id == user_id).first()
    
    if not user:
        session.close()
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    user.name = data['name']
    user.email = data['email']
    
    try:
        session.commit()
        redis_client.delete("users_list", f"user_{user_id}")
        session.close()
        return jsonify({"id": user.id, "name": user.name, "email": user.email})
    except IntegrityError:
        session.rollback()
        session.close()
        return jsonify({"error": "Email já existe"}), 400

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = get_session()
    user = session.query(User).filter(User.id == user_id).first()
    
    if not user:
        session.close()
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    session.delete(user)
    session.commit()
    redis_client.delete("users_list", f"user_{user_id}")
    session.close()
    return jsonify({"message": "Usuário deletado"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=False)