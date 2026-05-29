import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.database import Base, get_db
from datetime import datetime, timezone

# Configuração em memória do banco de dados para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(name="session")
def fixture_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def fixture_client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# Criação de um cliente com payload válido e salvamento no banco
def test_create_client(client):
    payload = {
        "cliente_nome": "Gabriel Antonin",
        "cliente_email": "gabriel.antonin@gmail.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 1000000,
    }
    response = client.post("/clientes", json=payload)
    assert response.status_code == 201
    assert response.json()["nome"] == payload["cliente_nome"]
    assert response.json()["status"] == "Aguardando Análise"


# Processamento do webhook aplicando a regra de prioridade correta com base no patrimônio
@pytest.mark.parametrize(
    "patrimonio, prioridade_esperada",
    [(250000, "prioridade_alta"), (180000, "prioridade_normal")],
)
def test_should_apply_correct_priority(client, patrimonio, prioridade_esperada):

    email = f"teste.{patrimonio}@gmail.com"
    client.post(
        "/clientes",
        json={
            "cliente_nome": "Teste",
            "cliente_email": email,
            "tipo_solicitacao": "Investimento Inicial",
            "valor_patrimonio": patrimonio,
        },
    )

    webhook_payload = {
        "event_id": f"evt_id_{patrimonio}",
        "card_id": "card_999",
        "cliente_email": email,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    assert response.status_code == 200
    assert response.json()["prioridade_definida"] == prioridade_esperada


# Bloqueio de processamento caso o event_id do webhook seja duplicado.
def test_should_block_process_duplicate_event_id(client):
    email = "teste@gmail.com"
    client.post(
        "/clientes",
        json={
            "cliente_nome": "Leticia Martins",
            "cliente_email": email,
            "tipo_solicitacao": "Atualização",
            "valor_patrimonio": 300000,
        },
    )

    webhook_payload = {
        "event_id": "evt_id_1",
        "card_id": "card_1",
        "cliente_email": email,
        "timestamp": "2026-05-18T12:00:00Z",
    }

    first_try = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    assert first_try.status_code == 200

    second_try = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    assert second_try.status_code == 409
    assert "Bloqueado" in second_try.json()["detail"]


# Teste de validação: e-mail inválido
def test_create_client_invalid_email(client):
    payload = {
        "cliente_nome": "Gabriel Antonin",
        "cliente_email": "e-mail-invalido",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 1000000,
    }
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422


# Teste de validação: campos obrigatórios ausentes
def test_create_client_missing_fields(client):
    payload = {
        "cliente_nome": "Gabriel Antonin",
        # campo cliente_email ausente
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 1000000,
    }
    response = client.post("/clientes", json=payload)
    assert response.status_code == 422