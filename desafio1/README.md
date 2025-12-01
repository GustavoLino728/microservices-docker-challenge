# Desafio 1 — Containers em Rede

## Descrição da Solução

Este desafio implementa dois containers Docker que se comunicam através de uma rede customizada:
- **Container Server**: Aplicação Flask expondo API REST na porta 8080
- **Container Client**: Script Python realizando requisições HTTP periódicas (a cada 5 segundos)

A comunicação ocorre através de uma rede bridge customizada, permitindo que os containers se identifiquem pelos nomes.

## Arquitetura

```
┌─────────────────────────────────────────┐
│     Rede: desafio1-network              │
│     Driver: bridge                      │
│                                         │
│  ┌──────────────┐   ┌──────────────┐   │
│  │    server    │   │    client    │   │
│  │              │   │              │   │
│  │ Flask:8080   │◄──│  requests    │   │
│  │              │   │  (loop 5s)   │   │
│  └──────────────┘   └──────────────┘   │
│         │                               │
└─────────┼───────────────────────────────┘
          │
          │ Port mapping
          ▼
      Host:8080
```

## Decisões Técnicas

1. **Flask como servidor web**: Escolhido por ser leve, fácil de implementar e ideal para APIs REST simples
2. **Python requests**: Biblioteca robusta para requisições HTTP com tratamento de erros
3. **Rede bridge customizada**: Permite comunicação por nome de container e isolamento dos containers
4. **Docker Compose**: Facilita orquestração e gerenciamento dos containers
5. **Intervalo de 5 segundos**: Balanceio entre demonstração clara e não sobrecarregar logs
6. **Nomenclatura em inglês**: Padronização seguindo boas práticas de desenvolvimento



## Funcionamento Detalhado

### Comunicação entre Containers

1. Ambos containers são conectados à rede `desafio1-network`
2. O Docker DNS resolve `server` para o IP interno do container servidor
3. Cliente faz requisição para `http://server:8080/status`
4. Servidor responde com JSON contendo timestamp, hostname e contador
5. Logs mostram a troca de mensagens em tempo real

### Endpoints da API

- `GET /status`: Retorna status do servidor com contador de requisições
- `GET /health`: Healthcheck simples

## Explicação do Código

**Servidor (`server/app.py`):**  
Utiliza Flask para criar uma API com dois endpoints. O `/status` retorna um JSON informando se o servidor está ativo, incluindo timestamp, hostname do container e um contador de requisições. A cada chamada, esse contador é incrementado. O endpoint `/health` serve para checagem rápida do estado do serviço. O servidor escuta em todas as interfaces, na porta 8080, facilitando o acesso pelo Docker.

**Cliente (`client/app.py`):**  
O cliente está em Python e usa a biblioteca `requests` para fazer chamadas HTTP ao servidor periodicamente, a cada 5 segundos. Se houver resposta, imprime no log o hostname do servidor e o total de requisições já processadas. O nome do container (`server`) é usado diretamente, aproveitando a resolução automática de nomes pela rede Docker.

**Dockerfiles:**  
Ambos os Dockerfiles usam Python 3.11 slim, copiam os requisitos, instalam dependências, transferem o script principal e definem o comando de inicialização. O Dockerfile do servidor expõe a porta 8080 para comunicação.

**docker-compose.yml:**  
O Compose define dois serviços (`server` e `client`) conectados à rede interna. O serviço do servidor expõe a porta 8080 para o host e ambos utilizam nomes fixos para facilitar a comunicação. O `depends_on` garante que o cliente só inicie após o servidor.

## Instruções de Execução

### Pré-requisitos
- Docker instalado (versão 20.10+)
- Docker Compose instalado

### Docker Compose

1. **Inicie os containers:**
   ```
   docker-compose up --build
   ```

2. **Para rodar em background:**
   ```
   docker-compose up -d --build
   ```

3. **Ver logs:**
   ```
   # Logs de ambos
   docker-compose logs -f
   
   # Apenas servidor
   docker-compose logs -f server
   
   # Apenas cliente
   docker-compose logs -f client
   ```

4. **Testar do host:**
   ```
   curl http://localhost:8080/status
   ```

5. **Parar e limpar:**
   ```
   docker-compose down
   ```

## Verificação da Rede

```
# Inspecionar rede e ver containers conectados
docker network inspect desafio1-network

# Ver status dos containers
docker ps
```

## Exemplo de Saída

### Logs do Cliente:
```
Cliente iniciado. Requisições a cada 5 segundos para http://server:8080/status
[2025-12-01 09:05:15] Requisição bem-sucedida | Servidor: a3f7b9c12d4e | Total: 1
[2025-12-01 09:05:20] Requisição bem-sucedida | Servidor: a3f7b9c12d4e | Total: 2
[2025-12-01 09:05:25] Requisição bem-sucedida | Servidor: a3f7b9c12d4e | Total: 3
```

### Logs do Servidor:
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
172.18.0.3 - - [01/Dec/2025 09:05:15] "GET /status HTTP/1.1" 200 -
172.18.0.3 - - [01/Dec/2025 09:05:20] "GET /status HTTP/1.1" 200 -
172.18.0.3 - - [01/Dec/2025 09:05:25] "GET /status HTTP/1.1" 200 -
```

### Teste via curl do host:
```
$ curl http://localhost:8080/status
{
  "hostname": "a3f7b9c12d4e",
  "requests_received": 4,
  "status": "online",
  "timestamp": "2025-12-01T09:05:30.123456"
}
```

## Comprovação de Comunicação

Para verificar que a comunicação está funcionando:

1. Os logs do cliente mostram as respostas do servidor
2. O contador de requisições incrementa a cada chamada
3. O hostname do servidor é exibido corretamente
4. Inspecionando a rede, ambos containers aparecem conectados:

```
docker network inspect desafio1-network
```

Saída esperada (trecho):
```
"Containers": {
    "xxx": {
        "Name": "server",
        "IPv4Address": "172.18.0.2/16"
    },
    "yyy": {
        "Name": "client",
        "IPv4Address": "172.18.0.3/16"
    }
}
```

## Estrutura do Projeto

```
desafio1/
├── README.md
├── docker-compose.yml
├── server/
│   ├── Dockerfile
│   ├── app.py            # Servidor Flask
│   └── requirements.txt
└── client/
    ├── Dockerfile
    ├── app.py            # Cliente com requests
    └── requirements.txt
```

## Tecnologias Utilizadas

- **Docker Engine**: Containerização
- **Docker Networks**: Comunicação entre containers
- **Docker Compose**: Orquestração de containers
- **Python 3.11**: Linguagem de programação
- **Flask 3.0**: Framework web
- **Requests 2.31**: Cliente HTTP