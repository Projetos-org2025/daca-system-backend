from sqlmodel import SQLModel, Field
from typing import Optional, Annotated

class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    login: Annotated[str, Field(min_length=3, max_length=50)]
    senha: Annotated[str, Field(min_length=3)]

class Veiculo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    placa: Annotated[str, Field(min_length=3)]
    marca: str
    modelo: str
    ano: Annotated[int, Field(ge=1900, le=2100)]
    login_cliente: Annotated[str, Field(min_length=3, max_length=50)]  # Dono do veículo
    imei: Annotated[str, Field(min_length=10, max_length=30)]          # IMEI do rastreador

class Localizacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    latitude: float
    longitude: float
    velocidade: float
    data_hora: str
    ignicao: str
    operadora: str
    endereco: Optional[str] = None
    login: Optional[str] = None
    placa: Optional[str] = None
