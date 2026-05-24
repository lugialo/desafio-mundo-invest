from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.controllers.schemas import ClientCreateSchema, WebhookPipefySchema
from app.models.database import engine, Base, get_db
from app.models import models  # noqa: F401
from app.services.services import ClientService, WebhookService

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Desafio Mundo Invest",
    description="API para cadastro de clientes e integração com Pipefy",
)


@app.post("/clientes", status_code=201)
def create_client(payload: ClientCreateSchema, db: Session = Depends(get_db)):
    client = ClientService.create_client(db, payload)
    return {
        "id": client.id,
        "nome": client.nome,
        "email": client.email,
        "tipo_solicitacao": client.tipo_solicitacao,
        "valor_patrimonio": client.valor_patrimonio,
        "status": client.status,
    }


@app.post("/webhooks/pipefy/card-updated", status_code=200)
def updated_card_webhook(payload: WebhookPipefySchema, db: Session = Depends(get_db)):
    result = WebhookService.process_update_card(db, payload)
    return result
