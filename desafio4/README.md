# Desafio 4 — Microsserviços Independentes

## Descrição da Solução

Este desafio implementa **dois microsserviços independentes** que se comunicam via HTTP:

- **Service A (Users Service)**: API que gerencia e retorna dados de usuários
- **Service B (Report Service)**: Consome Service A e gera relatórios formatados com informações combinadas

**Comunicação demonstrada**: Service B → HTTP → Service A (sem gateway intermediário)

## Arquitetura

```
┌──────────────────────────────────────────────────────┐
│           Rede: microservices-network                │
│                                                      │
│  ┌─────────────────────┐     ┌──────────────────┐   │
│  │   Service A         │     │   Service B      │   │
│  │   Users Service     │◄────│  Report Service  │   │
│  │   Flask :5001       │ HTTP│   Flask :5002    │   │
│  │                     │     │                  │   │
│  │  - GET /users       │     │ - GET /report    │   │
│  │  - GET /users/:id   │     │ - GET /report/:id│   │
│  └─────────────────────┘     └──────────────────┘   │
│           │                           │              │
└───────────┼───────────────────────────┼──────────────┘
            │                           │
       localhost:5001             localhost:5002
```

## Decisões Técnicas

1. **Microsserviços isolados**: Cada serviço tem seu próprio Dockerfile e responsabilidade única
2. **Comunicação HTTP**: Service B usa biblioteca `requests` para chamar Service A via DNS interno do Docker
3. **Dados simulados**: Users Service trabalha com dados em memória (lista Python) para simplificar demonstração
4. **Lógica de negócio no Service B**: Calcula dias de atividade e formata mensagens combinando dados
5. **Variáveis de ambiente**: URL do Service A configurável via `SERVICE_A_URL`
6. **Isolamento de portas**: Service A (5001) e Service B (5002) expõem portas diferentes

## Funcionamento Detalhado

### Fluxo de Comunicação

1. Cliente faz requisição para **Service B** (`http://localhost:5002/report`)
2. Service B envia requisição HTTP para **Service A** (`http://service-a:5001/users`)
3. Service A retorna JSON com lista de usuários
4. Service B processa dados:
   - Calcula dias desde cadastro usando `datetime`
   - Formata mensagem: "Usuário X ativo desde Y (Z dias)"
   - Combina informações de múltiplos campos
5. Service B retorna relatório formatado ao cliente

### Service A - Users Service

**Responsabilidades:**
- Gerenciar dados de usuários (CRUD básico)
- Expor endpoints REST para consulta
- Retornar dados brutos em JSON

**Endpoints:**
- `GET /health`: Healthcheck do serviço
- `GET /users`: Lista todos os usuários
- `GET /users/<id>`: Retorna usuário específico

**Dados armazenados:**
```
USERS = [
    {"id": 1, "name": "Jorge", "email": "jorge@example.com", "created_at": "2024-01-15"},
    {"id": 2, "name": "Mário", "email": "mario@example.com", "created_at": "2024-03-22"},
    {"id": 3, "name": "Carlos", "email": "carlos@example.com", "created_at": "2024-06-10"},
    {"id": 4, "name": "Maria", "email": "maria@example.com", "created_at": "2024-08-05"},
    {"id": 5, "name": "Gustavo Lino", "email": "gustavo@example.com", "created_at": "2024-11-20"}
]
```

### Service B - Report Service

**Responsabilidades:**
- Consumir dados do Service A
- Processar e enriquecer informações
- Gerar relatórios formatados

**Endpoints:**
- `GET /health`: Healthcheck do serviço
- `GET /report`: Relatório completo de todos os usuários
- `GET /report/<id>`: Relatório detalhado de usuário específico

**Lógica de processamento:**
```
def calculate_days_since(date_str):
    created = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.now()
    delta = today - created
    return delta.days
```

## Explicação do Código

### Service A (`service-a/app.py`)

**Endpoint principal:**
```
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({
        "service": "users-service",
        "total": len(USERS),
        "users": USERS
    })
```

Retorna lista completa de usuários com metadados. Dados armazenados em memória (lista Python) para simplicidade. Em produção, seria substituído por banco de dados.

**Busca individual:**
```
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in USERS if u["id"] == user_id), None)
```

Usa `next()` com generator expression para busca eficiente por ID.

### Service B (`service-b/app.py`)

**Consumo de microsserviço:**
```
response = requests.get(f"{SERVICE_A_URL}/users", timeout=5)
data = response.json()
users = data.get('users', [])
```

Faz requisição HTTP síncrona para Service A. A variável `SERVICE_A_URL` usa DNS do Docker para resolver `service-a` para o IP interno do container. Timeout de 5s previne travamento em caso de falha.

**Processamento e enriquecimento:**
```
for user in users:
    days_active = calculate_days_since(user['created_at'])
    
    report.append({
        "message": f"Usuário {user['name']} ativo desde {user['created_at']} ({days_active} dias)",
        "days_active": days_active
    })
```

Itera sobre usuários, calcula métrica adicional (dias ativos) e formata mensagem personalizada combinando múltiplos campos.

**Tratamento de erros:**
```
except requests.exceptions.ConnectionError:
    return jsonify({"error": "Não foi possível conectar ao Users Service"}), 503
```

Captura erro de conexão específico e retorna status 503 (Service Unavailable), indicando dependência indisponível.

## Instruções de Execução

### Pré-requisitos
- Docker Desktop
- Docker Compose V2+

### Execução

```
cd desafio4
docker-compose up --build
```

**URLs de acesso:**
- **Service A**: http://localhost:5001
- **Service B**: http://localhost:5002

### Testes da Comunicação

**1. Testar Service A diretamente:**
```
# Listar todos os usuários
curl http://localhost:5001/users

# Buscar usuário específico
curl http://localhost:5001/users/1
```

**Saída esperada (Service A):**
```
{
  "service": "users-service",
  "total": 5,
  "users": [
    {
      "id": 1,
      "name": "Jorge",
      "email": "jorge@example.com",
      "created_at": "2024-01-15"
    }
  ]
}
```

**2. Testar Service B (que consome Service A):**
```
# Relatório completo
curl http://localhost:5002/report

# Relatório de usuário específico
curl http://localhost:5002/report/5
```

**Saída esperada (Service B - Relatório completo):**
```
{
  "service": "report-service",
  "generated_at": "2025-12-02T08:26:00.123456",
  "total_users": 5,
  "report": [
    {
      "user_id": 1,
      "message": "Usuário Jorge ativo desde 2024-01-15 (322 dias)",
      "email": "jorge@example.com",
      "days_active": 322
    },
    {
      "user_id": 2,
      "message": "Usuário Mário ativo desde 2024-03-22 (256 dias)",
      "email": "mario@example.com",
      "days_active": 256
    },
    {
      "user_id": 5,
      "message": "Usuário Gustavo Lino ativo desde 2024-11-20 (12 dias)",
      "email": "gustavo@example.com",
      "days_active": 12
    }
  ]
}
```

**Saída esperada (Service B - Usuário específico):**
```
{
  "user_id": 5,
  "name": "Gustavo Lino",
  "email": "gustavo@example.com",
  "registered_on": "2024-11-20",
  "days_active": 12,
  "status": "Usuário Gustavo Lino ativo desde 2024-11-20 (12 dias)"
}
```

## Verificação da Rede

```
# Inspecionar rede Docker
docker network inspect desafio4_microservices-network

# Ver logs dos serviços
docker-compose logs -f service-a
docker-compose logs -f service-b

# Status dos containers
docker-compose ps
```

**Containers na rede:**
```
"Containers": {
  "service-a": {
    "Name": "users-service",
    "IPv4Address": "172.21.0.2/16"
  },
  "service-b": {
    "Name": "report-service",
    "IPv4Address": "172.21.0.3/16"
  }
}
```

## Estrutura do Projeto

```
desafio4/
├── README.md
├── docker-compose.yml          # Orquestração dos 2 microsserviços
├── service-a/
│   ├── Dockerfile             # Users Service
│   ├── app.py                # API de usuários
│   └── requirements.txt
└── service-b/
    ├── Dockerfile             # Report Service
    ├── app.py                # API de relatórios
    └── requirements.txt
```

## Comandos Úteis

```
# Reiniciar serviços
docker-compose restart

# Ver logs em tempo real
docker-compose logs -f

# Parar e remover tudo
docker-compose down

# Rebuild completo
docker-compose up --build --force-recreate
```

## Tecnologias Utilizadas

- **Docker**: Containerização de microsserviços
- **Docker Compose**: Orquestração e rede
- **Flask 3.0**: Framework web para APIs
- **Requests 2.31**: Cliente HTTP para comunicação
- **Python 3.11**: Linguagem de programação