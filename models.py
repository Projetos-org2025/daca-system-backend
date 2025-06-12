from sqlmodel import SQLModel, Field
from typing import Optional, Annotated

class Cliente(SQLModel, table=True):
id: Optional\[int] = Field(default=None, primary\_key=True)
login: Annotated\[str, Field(min\_length=3, max\_length=50)]
senha: Annotated\[str, Field(min\_length=3)]

class Veiculo(SQLModel, table=True):
id: Optional\[int] = Field(default=None, primary\_key=True)
placa: Annotated\[str, Field(min\_length=3)]
marca: str
modelo: str
ano: Annotated\[int, Field(ge=1900, le=2100)]
login\_cliente: Annotated\[str, Field(min\_length=3, max\_length=50)]  # Dono do veículo
imei: Annotated\[str, Field(min\_length=10, max\_length=30)]          # IMEI do rastreador

class Localizacao(SQLModel, table=True):
id: Optional\[int] = Field(default=None, primary\_key=True)
latitude: float
longitude: float
velocidade: float
data\_hora: str
ignicao: str
operadora: str
endereco: Optional\[str] = None
login: Optional\[str] = None
placa: Optional\[str] = None

class CoordenadaCache(SQLModel, table=True):
id: Optional\[int] = Field(default=None, primary\_key=True)
latitude: float
longitude: float
endereco: str
