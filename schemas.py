from pydantic import BaseModel, Field
from typing import Optional

# ✅ Schema para criação de cliente
class ClienteCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    senha: str = Field(..., min_length=3)
    marca: str
    modelo: str
    placa: str = Field(..., min_length=3)
    ano: int = Field(..., ge=1900, le=2100)

# ✅ Schema para envio de localização (funciona para rastreador ou celular)
class LocalizacaoCreate(BaseModel):
    imei: Optional[str] = None  # Rastreador envia isso
    placa: Optional[str] = None  # Celular usa isso (ex: CELULAR_FERNANDO)
    login: Optional[str] = None  # Para vincular ao cliente
    latitude: float
    longitude: float
    velocidade: float
    data_hora: str
    ignicao: str
    operadora: str
    endereco: Optional[str] = None

# ✅ Schema para cadastro de veículo
class VeiculoCreate(BaseModel):
    placa: str = Field(..., min_length=3)
    modelo: str
    marca: str
    ano: int = Field(..., ge=1900, le=2100)
    login_cliente: str = Field(..., min_length=3, max_length=50)
    imei: str = Field(..., min_length=10, max_length=30)  # ✅ Associado ao rastreador
