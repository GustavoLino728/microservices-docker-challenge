# Desafio 5 — Microsserviços com API Gateway

## Descrição da Solução

Este desafio implementa uma **arquitetura de microsserviços com API Gateway** como ponto único de entrada. O gateway centraliza e orquestra todas as requisições para os microsserviços internos:

- **API Gateway**: Ponto único de entrada exposto externamente (porta 8080)
- **Users Service**: Microsserviço interno para gerenciamento de usuários
- **Orders Service**: Microsserviço interno para gerenciamento de pedidos

**Vantagem chave**: Clientes externos só conhecem o gateway. Microsserviços internos não são expostos diretamente.

## Arquitetura

```
                    Cliente Externo
                          │
                          ▼
              ┌───────────────────────┐
              │   API Gateway         │
              │   :8080 (público)     │
              │                       │
              │  /users      /orders  │
              │  /health             │
              └───────────┬───────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │   Rede: gateway-network           │
        │                                   │
        │  ┌─────────────┐  ┌─────────────┐ │
        │  │ Users       │  │ Orders      │ │
        │  │ Service     │  │ Service     │ │
        │  │ :5001       │  │ :5002       │ │
        │  │ (interno)   │  │ (interno)   │ │
        │  └─────────────┘  └─────────────┘ │
        └───────────────────────────────────┘
```

## Decisões Técnicas

| Decisão | Justificativa |
|---------|---------------|
| **Gateway como proxy** | Centraliza autenticação, rate limiting, logging em um único ponto |
| **Serviços internos** | Não expõem portas externamente, apenas acessíveis via gateway na rede interna |
| **Roteamento baseado em path** | `/users/*` → Users Service, `/orders/*` → Orders Service |
| **Agregação de dados** | Endpoint `/users/{id}/orders` combina dados de múltiplos serviços |
| **Health check agregado** | Gateway verifica saúde de todos os serviços downstream |
| **Timeout configurado** | 5s para requisições, previne cascata de falhas |
| **Tratamento de erros** | Gateway retorna 503 quando serviço downstream está indisponível |

## Funcionamento Detalhado

### Fluxo de Requisição Simples

1. Cliente faz request: `GET http://localhost:8080/users`
2. Gateway recebe requisição no endpoint `/users`
3. Gateway roteia para `http://users-service:5001/users` (interno)
4. Users Service processa e retorna JSON
5. Gateway repassa resposta ao cliente

### Fluxo de Agregação (Bônus)

1. Cliente faz request: `GET http://localhost:8080/users/5/orders`
2. Gateway faz 2 requisições paralelas:
   - `GET http://users-service:5001/users/5`
   - `GET http://orders-service:5002/orders?user_id=5`
3. Gateway combina respostas em um único JSON
4. Cliente recebe dados agregados de ambos os serviços

### Isolamento de Serviços

**Serviços internos:**
- Não expõem portas para fora do Docker
- Apenas acessíveis via rede interna `gateway-network`
- DNS do Docker resolve nomes (`users-service`, `orders-service`)

**Gateway:**
- Única porta exposta: `8080:8080`
- Atua como reverse proxy
- Pode adicionar autenticação, rate limiting, CORS

## Explicação do Código

### API Gateway (`gateway/app.py`)

**Roteamento simples:**
```
@app.route('/users', methods=['GET'])
def get_users():
    response = requests.get(f"{USERS_SERVICE_URL}/users", timeout=5)
    return jsonify(response.json()), response.status_code
```

Gateway repassa requisição preservando método HTTP, query params e status code. Timeout de 5s evita travamento caso serviço downstream esteja lento.

**Health check agregado:**
```
@app.route('/health', methods=['GET'])
def health():
    health_status = {"gateway": "ok"}
    
    try:
        users_health = requests.get(f"{USERS_SERVICE_URL}/health", timeout=2)
        health_status["users-service"] = "ok" if users_health.status_code == 200 else "error"
    except:
        health_status["users-service"] = "unreachable"
```

Verifica saúde de todos os serviços downstream em uma única chamada. Útil para monitoramento e health checks de infraestrutura.

**Agregação de dados:**
```
@app.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_with_orders(user_id):
    # Busca usuário
    user_response = requests.get(f"{USERS_SERVICE_URL}/users/{user_id}")
    user_data = user_response.json()
    
    # Busca pedidos do usuário
    orders_response = requests.get(f"{ORDERS_SERVICE_URL}/orders?user_id={user_id}")
    orders_data = orders_response.json()
    
    # Combina resultados
    return jsonify({"user": user_data, "orders": orders_data.get("orders", [])})
```

Gateway faz múltiplas requisições e agrega resultados. Cliente faz 1 chamada ao invés de 2, reduzindo latência e simplificando lógica do frontend.

### Users Service (`users-service/app.py`)

```
USERS = [
    {"id": 1, "name": "Jorge", "email": "jorge@example.com", "status": "active"},
    {"id": 2, "name": "Mário", "email": "mario@example.com", "status": "active"},
    {"id": 3, "name": "Carlos", "email": "carlos@example.com", "status": "inactive"},
    {"id": 4, "name": "Maria", "email": "maria@example.com", "status": "active"},
    {"id": 5, "name": "Gustavo", "email": "gustavo@example.com", "status": "active"}
]
```

Serviço responsável apenas por gerenciar usuários. Não sabe da existência de outros serviços. Porta 5001 não exposta externamente.

### Orders Service (`orders-service/app.py`)

```
@app.route('/orders', methods=['GET'])
def get_orders():
    user_id = request.args.get('user_id', type=int)
    
    if user_id:
        filtered = [o for o in ORDERS if o["user_id"] == user_id]
        return jsonify({"orders": filtered})
```

Suporta filtragem por `user_id` via query parameter. Gateway usa esse recurso para agregação.

## Instruções de Execução

### Pré-requisitos
- Docker Desktop
- Docker Compose V2+

### Execução

```
cd desafio5
docker-compose up --build
```

**URLs de acesso:**
- **Gateway (único ponto de entrada)**: http://localhost:8080
- **Users Service**: Não acessível externamente (apenas interno)
- **Orders Service**: Não acessível externamente (apenas interno)

### Testes via Gateway

**1. Health check agregado:**
```
curl http://localhost:8080/health
```

**Resposta esperada:**
```
{
  "gateway": "ok",
  "users-service": "ok",
  "orders-service": "ok"
}
```

**2. Listar todos os usuários:**
```
curl http://localhost:8080/users
```

**Resposta:**
```
{
  "service": "users-service",
  "total": 5,
  "users": [
    {"id": 1, "name": "Jorge", "email": "jorge@example.com", "status": "active"},
    {"id": 5, "name": "Gustavo", "email": "gustavo@example.com", "status": "active"}
  ]
}
```

**3. Buscar usuário específico:**
```
curl http://localhost:8080/users/5
```

**Resposta:**
```
{
  "id": 5,
  "name": "Gustavo",
  "email": "gustavo@example.com",
  "status": "active"
}
```

**4. Listar todos os pedidos:**
```
curl http://localhost:8080/orders
```

**5. Filtrar pedidos por usuário:**
```
curl http://localhost:8080/orders?user_id=5
```

**Resposta:**
```
{
  "service": "orders-service",
  "user_id": 5,
  "total": 2,
  "orders": [
    {"id": 105, "user_id": 5, "product": "Headset Gamer", "amount": 320.0, "status": "delivered"},
    {"id": 106, "user_id": 5, "product": "Webcam HD", "amount": 280.0, "status": "pending"}
  ]
}
```

**6. Buscar pedido específico:**
```
curl http://localhost:8080/orders/105
```

**7. Agregação - Usuário + Pedidos (BÔNUS):**
```
curl http://localhost:8080/users/5/orders
```

**Resposta agregada:**
```
{
  "user": {
    "id": 5,
    "name": "Gustavo",
    "email": "gustavo@example.com",
    "status": "active"
  },
  "orders": [
    {"id": 105, "user_id": 5, "product": "Headset Gamer", "amount": 320.0, "status": "delivered"},
    {"id": 106, "user_id": 5, "product": "Webcam HD", "amount": 280.0, "status": "pending"}
  ],
  "total_orders": 2
}

## Verificação da Arquitetura

**Confirmar que serviços internos não são acessíveis:**
```
# Estas requisições devem FALHAR (serviços não expostos)
curl http://localhost:5001/users  # Connection refused
curl http://localhost:5002/orders # Connection refused

# Apenas o gateway deve responder
curl http://localhost:8080/users  # ✓ Funciona
```

**Inspecionar rede Docker:**
```
docker network inspect desafio5_gateway-network
```

**Saída esperada:**
```
"Containers": {
  "api-gateway": {"IPv4Address": "172.22.0.4/16"},
  "users-service": {"IPv4Address": "172.22.0.2/16"},
  "orders-service": {"IPv4Address": "172.22.0.3/16"}
}
```

## Estrutura do Projeto

```
desafio5/
├── README.md
├── docker-compose.yml              # Orquestração 3 serviços
├── gateway/
│   ├── Dockerfile                 # API Gateway
│   ├── app.py                    # Proxy + Agregação
│   └── requirements.txt
├── users-service/
│   ├── Dockerfile                 # Microsserviço Usuários
│   ├── app.py                    # CRUD Usuários
│   └── requirements.txt
└── orders-service/
    ├── Dockerfile                 # Microsserviço Pedidos
    ├── app.py                    # CRUD Pedidos
    └── requirements.txt
```

## Benefícios do API Gateway

| Benefício | Descrição |
|-----------|-----------|
| **Ponto único** | Clientes só conhecem uma URL |
| **Segurança** | Autenticação/autorização centralizada |
| **Rate limiting** | Controle de requisições em um lugar |
| **Logging** | Monitoramento centralizado de todas as requisições |
| **Versionamento** | `/v1/users`, `/v2/users` roteados para serviços diferentes |
| **Agregação** | Reduz round-trips cliente-servidor |
| **Isolamento** | Mudanças internas não afetam clientes |

## Comandos Úteis

```
# Logs do gateway
docker-compose logs -f gateway

# Logs de todos os serviços
docker-compose logs -f

# Reiniciar apenas gateway
docker-compose restart gateway

# Parar e remover tudo
docker-compose down

# Rebuild completo
docker-compose up --build --force-recreate
```

## Tecnologias Utilizadas

- **Docker Compose**: Orquestração de containers
- **Flask 3.0**: Framework web para APIs
- **Requests 2.31**: Cliente HTTP para proxy
- **Python 3.11**: Linguagem de programação
- **Docker Networks**: Isolamento e DNS interno