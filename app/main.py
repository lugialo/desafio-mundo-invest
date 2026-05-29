from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.controllers.controllers import create_client, updated_card_webhook
from app.controllers.schemas import ClientCreateSchema, WebhookPipefySchema
from app.models.database import engine, Base, get_db
from app.models import models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Desafio Mundo Invest",
    description="API para cadastro de clientes e integração com Pipefy",
)


@app.post("/clientes", status_code=201)
def create_client_endpoint(payload: ClientCreateSchema, db: Session = Depends(get_db)):
    return create_client(payload, db)


@app.post("/webhooks/pipefy/card-updated", status_code=200)
def updated_card_webhook_endpoint(
    payload: WebhookPipefySchema, db: Session = Depends(get_db)
):
    return updated_card_webhook(payload, db)
