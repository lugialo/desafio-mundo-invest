from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.controllers.schemas import ClientCreateSchema
from app.models.models import ClientModel
from app.integrations.pipefy_client import PipefyClient


class ClientService:

    @staticmethod
    def create_client(db: Session, payload: ClientCreateSchema):
        existing_client = (
            db.query(ClientModel)
            .filter(ClientModel.email == payload.cliente_email)
            .first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="Um cliente com este e-mail já está cadastrado.",
            )

        new_client = ClientModel(
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
