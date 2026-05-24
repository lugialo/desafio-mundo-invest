from pydantic import BaseModel, EmailStr
from datetime import datetime

class ClientCreateSchema(BaseModel):
    cliente_nome: str
    cliente_email: EmailStr # classe de validação de email do pydantic
    tipo_solicitacao: str
    valor_patrimonio: float

    class Config:
        from_attributes = True
        
class WebhookPipefySchema(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: datetime
        