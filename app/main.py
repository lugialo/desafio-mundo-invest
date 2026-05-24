from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.controllers.schemas import ClientCreateSchema
from app.models.database import engine, Base, get_db
from app.models import models  # noqa: F401
from app.services.services import ClientService

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
