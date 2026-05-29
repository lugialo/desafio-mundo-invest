# Desafio Técnico — Client Management & Pipefy Integration

Sistema interno para o Mundo Invest gerenciar clientes e patrimônios, com integração ao Pipefy via mutations GraphQL simuladas.

---

## Rodando o projeto


### Requisitos
- Python 3.10+
- uv (opcional)

```bash
# Clone e acesse o repositório
git clone https://github.com/lugialo/desafio-mundo-invest.git
cd desafio-mundo-invest

# Crie o venv e ative
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instale as dependências
pip install .
# ou, se usar uv:
uv sync

# Suba o servidor
uvicorn app.main:app --reload
```

Acesse em `http://127.0.0.1:8000`.

---

## Testes

Os testes usam `pytest` com SQLite em memória (`sqlite:///:memory`):

```bash
pytest
# ou
uv run pytest
```

---

## Exemplos de uso

### Criar um cliente

Cria o registro com status `"Aguardando Análise"` e simula o `createCard` no Pipefy.

```bash
curl -X POST http://127.0.0.1:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "Gabriel Antonin",
    "cliente_email": "gabriel@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }'
```

```json
// HTTP 201
{
  "id": 1,
  "nome": "Gabriel Antonin",
  "email": "gabriel@example.com",
  "tipo_solicitacao": "Atualização cadastral",
  "valor_patrimonio": 250000.0,
  "status": "Aguardando Análise"
}
```

### Webhook de atualização de card

```bash
curl -X POST http://127.0.0.1:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_123",
    "cliente_email": "gabriel@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }'
```

```json
// HTTP 200 — sucesso
{ "message": "Webhook processado", "prioridade_definida": "prioridade_alta" }

// HTTP 409 — evento duplicado
{ "detail": "Bloqueado: Evento já processado. 'evt_123'" }
```

---

## Visão de Produção (AWS)

### Diagrama de arquitetura

<img width="2758" height="1293" alt="Untitled" src="https://github.com/user-attachments/assets/8636b856-7b4a-4b8e-ba2e-d33aac9f1e6b" />


---

### Fluxo 1 — `POST /clientes`

O **API Gateway** recebe a requisição e a repassa diretamente para o **`CreateClientLambda`**, uma função Lambda responsável por:

- Validar o payload e o formato do e-mail
- Persistir o cliente no **RDS PostgreSQL** via **RDS Proxy**
- Montar a mutation `createCard` do Pipefy

---

### Fluxo 2 — `POST /webhooks/pipefy/card-updated`

O **API Gateway** recebe o evento do Pipefy e enfileira no **SQS** antes de acionar o **`PipefyWebhookLambda`**. Essa etapa de filas tem dois benefícios diretos: absorve picos de volume sem perder eventos e garante reprocessamento automático em caso de falha do Lambda.

O `PipefyWebhookLambda` executa a seguinte sequência:

1. **Idempotência**: consulta o **DynamoDB** pelo `event_id`. Se já existir, retorna `HTTP 409` sem processar nada.
2. **Gravação atômica**: registra o `event_id` no DynamoDB com tempo de vida de 30 dias.
3. **Regra de prioridade**: busca o cliente no **RDS PostgreSQL** pelo `cliente_email` e calcula:
   - `valor_patrimonio >= 200.000` → `prioridade_alta`
   - `valor_patrimonio < 200.000` → `prioridade_normal`
4. **Persistência**: atualiza o status do cliente para `"Processado"` e salva a prioridade no RDS.
5. **Pipefy**: monta a mutation `updateCardField`.

---

