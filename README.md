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
