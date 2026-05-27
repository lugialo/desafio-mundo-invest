from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime
from app.models.database import Base


class Client(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    tipo_solicitacao = Column(String, nullable=False)
    valor_patrimonio = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="Aguardando Análise")
    prioridade = Column(String, nullable=True)


class ProcessedEvent(Base):
    __tablename__ = "eventos_processados"

    event_id = Column(String, primary_key=True, index=True)
    processed_at = Column(DateTime)
