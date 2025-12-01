import psycopg2
import time
import os
from datetime import datetime

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'database': os.getenv('DB_NAME', 'mydb'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'admin123')
}

def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro ao conectar: {e}")
        return None

def read_users():
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        
        print(f"\n{'='*60}")
        print(f"Total de usuários no banco: {len(users)}")
        print(f"{'='*60}")
        
        for user in users:
            print(f"ID: {user[0]} | Nome: {user[1]} | Email: {user[2]}")
        
        # Registrar acesso
        cursor.execute("INSERT INTO access_logs (action) VALUES ('Data read by reader')")
        conn.commit()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao ler dados: {e}")

def main():
    print("Reader iniciado. Aguardando banco de dados...")
    time.sleep(5)
    
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{timestamp}] Lendo dados do banco...")
        read_users()
        time.sleep(10)

if __name__ == '__main__':
    main()