# Desafio 2 — Volumes e Persistência

## Descrição da Solução

Este desafio demonstra o uso de volumes Docker para persistência de dados. Mesmo após remover e recriar containers, os dados permanecem intactos no volume. A solução inclui:
- **PostgreSQL**: Banco de dados com volume persistente
- **Script de inicialização**: Cria tabelas e insere dados iniciais
- **Container Reader**: Lê dados periodicamente, demonstrando persistência

## Arquitetura

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  ┌────────────┐          ┌──────────────┐       │
│  │  postgres  │          │    reader    │       │
│  │  (port     │◄─────────│              │       │
│  │   5432)    │  query   │  psycopg2    │       │
│  └─────┬──────┘          └──────────────┘       │
│        │                                         │
│        │ monta                                   │
│        ▼                                         │
│  ┌──────────────────────┐                       │
│  │  Volume Nomeado:     │                       │
│  │  postgres-data       │                       │
│  │  (persistente)       │                       │
│  └──────────────────────┘                       │
│         Host File System                         │
└──────────────────────────────────────────────────┘
```

## Decisões Técnicas

1. **PostgreSQL**: Banco de dados robusto e amplamente utilizado
2. **Volume nomeado**: Facilita gerenciamento e identificação
3. **Alpine Linux**: Imagem menor (postgres:15-alpine ~80MB vs ~130MB)
4. **Script de inicialização**: `/docker-entrypoint-initdb.d` executa automaticamente na primeira vez
5. **Container reader**: Demonstra leitura dos dados persistentes de forma visual
6. **Variáveis de ambiente**: Configuração flexível das credenciais

## Funcionamento Detalhado

### Persistência de Dados

1. Volume `postgres-data` é criado e montado em `/var/lib/postgresql/data`
2. Todos os dados do PostgreSQL são armazenados neste volume
3. Ao remover o container, o volume permanece no host
4. Ao recriar o container com o mesmo volume, os dados são restaurados

### Inicialização do Banco

1. Na primeira execução, PostgreSQL executa `init.sql` automaticamente
2. Cria tabelas `users` e `access_logs`
3. Insere 4 usuários de exemplo
4. Em execuções posteriores, o script não é executado novamente (dados já existem)

### Container Reader

1. Conecta ao PostgreSQL usando psycopg2
2. Lê todos os usuários da tabela a cada 10 segundos
3. Registra cada leitura na tabela `access_logs`
4. Demonstra que múltiplos containers podem acessar os mesmos dados

## Explicação do Código

**init.sql:**  
Script SQL executado automaticamente na inicialização do PostgreSQL. Cria duas tabelas: `users` (com dados de exemplo) e `access_logs` (para rastrear acessos). O PostgreSQL só executa scripts em `/docker-entrypoint-initdb.d` quando o volume está vazio.

**reader/app.py:**  
Script Python que conecta ao PostgreSQL usando credenciais de variáveis de ambiente. A função `connect_db()` estabelece conexão, e `read_users()` executa uma query SELECT para buscar todos os usuários. Cada leitura também insere um registro em `access_logs`, demonstrando escrita no banco. O loop principal executa a cada 10 segundos.

**docker-compose.yml:**  
Define o serviço PostgreSQL com volume nomeado `postgres-data` montado no diretório de dados do banco. A pasta `init-db` é montada em `/docker-entrypoint-initdb.d` para execução automática. O reader depende do postgres e usa as mesmas credenciais via variáveis de ambiente. Ambos conectados à rede bridge customizada.

## Instruções de Execução

### Pré-requisitos
- Docker instalado (versão 20.10+)
- Docker Compose instalado

### Passo 1: Primeira Execução (Criar Dados)

1. **Inicie os containers:**
   ```
   docker-compose up -d
   ```

2. **Verifique os logs:**
   ```
   docker-compose logs -f reader
   ```

3. **Conecte ao banco manualmente (opcional):**
   ```
   docker exec -it postgres-db psql -U admin -d mydb
   ```
   
   Dentro do psql:
   ```
   SELECT * FROM users;
   SELECT * FROM access_logs;
   \q
   ```

### Passo 2: Demonstrar Persistência

1. **Pare e remova os containers:**
   ```
   docker-compose down
   ```
   
   ⚠️ **Importante**: Isso remove os containers mas NÃO remove o volume!

2. **Verifique que o volume ainda existe:**
   ```
   docker volume ls | grep desafio2
   ```
   
   Saída esperada:
   ```
   local     desafio2-postgres-data
   ```

3. **Recrie os containers:**
   ```
   docker-compose up -d
   ```

4. **Verifique que os dados persistiram:**
   ```
   docker-compose logs reader
   ```
   
   Os mesmos 4 usuários devem aparecer!

5. **Verifique os logs de acesso:**
   ```
   docker exec -it postgres-db psql -U admin -d mydb -c "SELECT * FROM access_logs;"
   ```
   
   Deve mostrar registros antes e depois da recriação do container.

### Passo 3: Adicionar Novos Dados

1. **Adicione um novo usuário:**
   ```
   docker exec -it postgres-db psql -U admin -d mydb -c "INSERT INTO users (name, email) VALUES ('Eva Martins', 'eva@example.com');"
   ```

2. **Verifique no reader:**
   ```
   docker-compose logs -f reader
   ```
   
   Agora deve mostrar 5 usuários!

3. **Repita o teste de persistência:**
   ```
   docker-compose down
   docker-compose up -d
   docker-compose logs reader
   ```
   
   O usuário Eva deve estar presente!

### Comandos Úteis

```
# Inspecionar o volume
docker volume inspect desafio2-postgres-data

# Ver tamanho do volume
docker system df -v | grep desafio2

# Backup do volume
docker run --rm -v desafio2-postgres-data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres-backup.tar.gz /data

# Limpar TUDO (incluindo volume)
docker-compose down -v

# Listar todos os volumes
docker volume ls
```

## Comprovação de Persistência

![Imagem Processo de Persistência](image.png)

### Teste Realizado:

1. **Primeira execução:**
   ```
   Total de usuários no banco: 4
   ID: 1 | Nome: Alice Silva | Email: alice@example.com
   ID: 2 | Nome: Bruno Santos | Email: bruno@example.com
   ID: 3 | Nome: Carla Oliveira | Email: carla@example.com
   ID: 4 | Nome: Daniel Costa | Email: daniel@example.com
   ```

2. **Após `docker-compose down` e `up`:**
   ```
   Total de usuários no banco: 4
   [Mesmos dados acima]
   ```

3. **Logs de acesso confirmam persistência:**
   ```
   id |          action           |         timestamp
   ----+---------------------------+----------------------------
    1 | Database initialized      | 2025-12-01 09:57:10.123
    2 | Data read by reader       | 2025-12-01 09:57:15.456
    3 | Data read by reader       | 2025-12-01 10:05:20.789
   ```

### Onde os Dados Estão?

Execute:
```
docker volume inspect desafio2-postgres-data
```

Saída:
```
{
    "Name": "desafio2-postgres-data",
    "Driver": "local",
    "Mountpoint": "/var/lib/docker/volumes/desafio2-postgres-data/_data"
}
```

Os dados estão em `/var/lib/docker/volumes/desafio2-postgres-data/_data` no host.

## Estrutura do Projeto

```
desafio2/
├── README.md
├── docker-compose.yml
├── init-db/
│   └── init.sql          # Script de inicialização do banco
└── reader/
    ├── Dockerfile
    ├── app.py            # Container que lê dados
    └── requirements.txt
```

## Tecnologias Utilizadas

- **Docker Volumes**: Persistência de dados
- **PostgreSQL 15**: Banco de dados relacional
- **Python 3.11**: Linguagem de programação
- **psycopg2**: Driver PostgreSQL para Python
- **Docker Compose**: Orquestração

## Execute com:

```bash
docker-compose up -d
docker-compose logs -f reader
```

Para testar persistência:
```bash
docker-compose down
docker-compose up -d
```

