from sqlalchemy.orm import Session

from app.controllers.schemas import ClientCreateSchema, WebhookPipefySchema
from app.services.services import ClientService, WebhookService


def create_client(payload: ClientCreateSchema, db: Session):
    client = ClientService.create_client(db, payload)
    return {
        "id": client.id,
        "nome": client.nome,
        "email": client.email,
        "tipo_solicitacao": client.tipo_solicitacao,
        "valor_patrimonio": client.valor_patrimonio,
        "status": client.status,
    }


def updated_card_webhook(payload: WebhookPipefySchema, db: Session):
    result = WebhookService.process_update_card(db, payload)
    return result
