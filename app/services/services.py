from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.controllers.schemas import ClientCreateSchema, WebhookPipefySchema
from app.models.models import Client, ProcessedEvent
from app.integrations.pipefy_client import PipefyClient


class ClientService:

    @staticmethod
    def create_client(db: Session, payload: ClientCreateSchema):
        existing_client = (
            db.query(Client).filter(Client.email == payload.cliente_email).first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="Um cliente com este e-mail já está cadastrado.",
            )

        new_client = Client(
            nome=payload.cliente_nome,
            email=payload.cliente_email,
            tipo_solicitacao=payload.tipo_solicitacao,
            valor_patrimonio=payload.valor_patrimonio,
            status="Aguardando Análise",
        )
        db.add(new_client)
        db.commit()
        db.refresh(new_client)

        payload_graphql = PipefyClient.simulate_create_card(
            nome=payload.cliente_nome,
            email=payload.cliente_email,
            valor_patrimonio=payload.valor_patrimonio,
        )

        print(f"\n--- Mutation enviada para createCard ---\n{payload_graphql}\n")

        return new_client


class WebhookService:

    @staticmethod
    def process_update_card(db: Session, payload: WebhookPipefySchema):

        # verifica se o evento já foi processado
        existing_event = (
            db.query(ProcessedEvent)
            .filter(ProcessedEvent.event_id == payload.event_id)
            .first()
        )
        if existing_event:
            raise HTTPException(
                status_code=409, detail=f"Bloqueado: Evento já processado. '{payload.event_id}'"
            )

        new_event = ProcessedEvent(
            event_id=payload.event_id, processed_at=payload.timestamp
        )
        db.add(new_event)

        client = db.query(Client).filter(Client.email == payload.cliente_email).first()
        if not client:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente informado no webhook não foi localizado no banco local.",
            )

        # Definição da prioridade com base no valor do patrimônio
        if client.valor_patrimonio >= 200000:
            prioridade_calculada = "prioridade_alta"
        else:
            prioridade_calculada = "prioridade_normal"

        client.status = "Processado"
        client.prioridade = prioridade_calculada

        db.commit()

        payload_graphql = PipefyClient.simulate_update_card_fields(
            card_id=payload.card_id, status="Processado", prioridade=prioridade_calculada
        )

        print(
            f"\n--- [PIPEFY INTERACTION] Mutations/Payloads Pipefy ---\n{payload_graphql}\n"
        )

        return {"message": "Webhook processado", "prioridade_definida": prioridade_calculada}
