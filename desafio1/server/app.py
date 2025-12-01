from flask import Flask, jsonify
from datetime import datetime
import socket

app = Flask(__name__)
request_count = 0

@app.route('/status', methods=['GET'])
def status():
    global request_count
    request_count += 1
    
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'hostname': socket.gethostname(),
        'requests_received': request_count
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'health': 'ok', 'service': 'web-server'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)