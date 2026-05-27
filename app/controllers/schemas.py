from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class ClientCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cliente_nome: str
    cliente_email: EmailStr  # classe de validação de email do pydantic
    tipo_solicitacao: str
    valor_patrimonio: float


class WebhookPipefySchema(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: datetime
