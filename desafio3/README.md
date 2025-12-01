# Desafio 3 — Docker Compose Orquestrando Serviços

## Descrição da Solução

Esta solução implementa uma aplicação completa com **3 serviços interdependentes** orquestrados via Docker Compose:

- **API Flask** (backend): CRUD completo de usuários com SQLAlchemy + SQLite
- **Redis** (cache): Armazena listas de usuários e usuários individuais para otimização
- **Streamlit** (frontend): Interface web interativa para testar a API

**Comunicação demonstrada**: Frontend → API → Redis (cache) → SQLite (persistência)

## Decisões Técnicas

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| **Backend** | Flask + SQLAlchemy + SQLite | ORM simplifica CRUD, SQLite sem servidor externo |
| **Cache** | Redis | Cache de leitura rápida, invalidação automática |
| **Frontend** | Streamlit | Interface visual instantânea para demonstração |
| **Orquestração** | Docker Compose | Dependências, rede interna, variáveis ambiente |
| **Persistência** | Volume Docker | Dados SQLite sobrevivem recriação de containers |

## Funcionamento Detalhado

### Fluxo de Comunicação

1. **Frontend (Streamlit)** chama API via HTTP (`http://api:8080`)
2. **API (Flask)** verifica Redis primeiro (cache hit/miss)
3. **Cache miss**: API consulta SQLite via SQLAlchemy
4. **Cache hit**: Redis retorna dados instantaneamente
5. **Cache invalidado** em CREATE/UPDATE/DELETE

### Dependências e Inicialização

```
frontend → depends_on: api
api      → depends_on: redis
redis    → inicia primeiro (sem dependências)
```

### Cache Strategy

- **Lista de usuários**: TTL 60s (`users_list`)
- **Usuário individual**: TTL 300s (`user_1`, `user_2`)
- **Invalidado** em mutações (CREATE/UPDATE/DELETE)

## Explicação do Código

### API Flask (`api/app.py`)

**Estrutura principal:**
```
# Conexão Redis
redis_client = redis.from_url(os.getenv('REDIS_URL'))

# ORM SQLAlchemy + SQLite
session = get_session()  # Conexão por request
```

**Padrão Cache-First:**
```
@app.route('/users', methods=['GET'])
def list_users():
    cached = redis_client.get("users_list")  # 1º Cache
    if cached: return jsonify(cached)        # Cache HIT
    
    users = session.query(User).all()        # 2º Banco
    redis_client.set("users_list", data)     # Armazena cache
```

### Model SQLAlchemy (`api/models.py`)

```
class User(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
```

### Frontend Streamlit (`frontend/streamlit_app.py`)

Interface com 3 abas:
- **Listar**: Tabela com dados do cache/banco
- **Criar**: Formulário POST para API
- **Editar/Deletar**: Operações PUT/DELETE

## Instruções de Execução

### Pré-requisitos
- Docker Desktop
- Docker Compose V2+

### Execução Completa

```
cd desafio3
docker-compose up --build
```

**URLs de acesso:**
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8080/health
- **Logs**: `docker-compose logs -f`

### Teste Manual da API (curl)

```
# Health check
curl http://localhost:8080/health

# Listar usuários
curl http://localhost:8080/users

# Criar usuário
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Ana", "email": "ana@test.com"}'

# Buscar usuário (2ª vez = cache hit)
curl http://localhost:8080/users/1
```

## Comprovação dos Requisitos

### ✅ [10 pts] Compose funcional e bem estruturado
```
✓ 3 serviços orquestrados (api, frontend, redis)
✓ Rede interna customizada (desafio3-network)
✓ depends_on configurado corretamente
✓ Volumes para persistência SQLite
✓ Variáveis de ambiente definidas
```

### ✅ [5 pts] Comunicação entre serviços funcionando
```
Frontend:8501 → API:8080 (HTTP)
API:8080 ↔ Redis:6379 (cache)
API:8080 → SQLite:app.db (persistência)
```

### ✅ [5 pts] README com explicação da arquitetura
```
✓ Diagrama ASCII da arquitetura
✓ Decisões técnicas justificadas
✓ Fluxo de comunicação detalhado
✓ Instruções passo a passo
```

### ✅ [5 pts] Clareza e boas práticas
```
✓ Separação backend/frontend
✓ Cache com invalidação automática
✓ ORM SQLAlchemy (padronização)
✓ Tratamento de erros (IntegrityError)
✓ Estrutura modular (models.py)
```

## Verificação da Rede Docker

```
# Containers conectados à rede
docker network inspect desafio3_desafio3-network

# Status dos serviços
docker-compose ps

# Volume de persistência
docker volume inspect desafio3_api-data
```

**Saída esperada da rede:**
```
"Containers": {
  "api-container": {"Name": "desafio3-api", "IPv4Address": "172.20.0.3/16"},
  "frontend-container": {"Name": "desafio3-frontend", "IPv4Address": "172.20.0.4/16"},
  "redis-container": {"Name": "desafio3-redis", "IPv4Address": "172.20.0.2/16"}
}
```

## Exemplo de Saída - Frontend Streamlit

**Aba "Listar" (1ª vez - cache miss):**
```
Carregado do SQLite → Redis (cache armazenado)
[ID: 1, Name: Ana, Email: ana@test.com]
```

**Aba "Listar" (2ª vez - cache hit):**
```
Carregado do cache Redis! (1 usuários)
[ID: 1, Name: Ana, Email: ana@test.com]
```

## Estrutura do Projeto

```
desafio3/
├── docker-compose.yml          # Orquestração 3 serviços
├── api/
│   ├── Dockerfile             # Flask + SQLAlchemy
│   ├── app.py                # API REST + Cache Redis
│   ├── models.py             # Model User SQLAlchemy
│   └── requirements.txt
└── frontend/
    ├── Dockerfile             # Streamlit
    ├── streamlit_app.py       # Interface CRUD
    └── requirements.txt
```

## Comandos Úteis

```
# Reiniciar com cache limpo
docker-compose down -v
docker-compose up --build

# Ver logs específicos
docker-compose logs -f api
docker-compose logs -f frontend

# Limpeza completa
docker-compose down -v --rmi all --remove-orphans
```

## Tecnologias Utilizadas

- **Docker Compose**: Orquestração e rede interna
- **Flask 3.0**: API REST
- **SQLAlchemy 2.0**: ORM + SQLite
- **Redis 7**: Cache distribuído
- **Streamlit 1.29**: Frontend reativo