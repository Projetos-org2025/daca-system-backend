from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import criar_banco, get_session
from schemas import ClienteCreate, LocalizacaoCreate, VeiculoCreate
from crud import (
    criar_cliente, buscar_cliente_por_login,
    criar_veiculo, buscar_veiculo_por_imei,
    salvar_localizacao_db
)
from models import Localizacao, Veiculo
import requests

app = FastAPI()
criar_banco()

# ✅ Middleware CORS para permitir acesso do mapa.html hospedado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou especifique ["https://seusite.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/mapa.html")
def abrir_mapa():
    return FileResponse("static/mapa.html")

# ------------------ CLIENTE ------------------

@app.post("/registrar")
def registrar(cliente: ClienteCreate, session: Session = Depends(get_session)):
    return criar_cliente(session, cliente)

@app.get("/cliente/{login}")
def obter_cliente(login: str, session: Session = Depends(get_session)):
    return buscar_cliente_por_login(session, login)

# ------------------ VEÍCULO ------------------

@app.post("/cadastrar_veiculo")
def cadastrar_veiculo(veiculo: VeiculoCreate, session: Session = Depends(get_session)):
    return criar_veiculo(session, veiculo)

@app.get("/veiculos/{login}")
def veiculos_cliente(login: str, session: Session = Depends(get_session)):
    login = login.strip().lower()
    stmt = select(Veiculo).where(Veiculo.login_cliente.ilike(login))
    resultado = session.exec(stmt).all()
    return resultado

# ------------------ GEOLOCALIZAÇÃO ------------------

def obter_endereco_real(lat: float, lon: float) -> str:
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=pt-BR"
        headers = {
            "User-Agent": "DacaSystem/1.0 (contato@dacasystem.com)"
        }
        resposta = requests.get(url, headers=headers, timeout=10)
        if resposta.status_code == 200:
            dados = resposta.json()
            return dados.get("display_name", "Endereço não encontrado")
        else:
            return "Endereço não encontrado"
    except Exception:
        return "Erro ao obter endereço"

# ------------------ LOCALIZAÇÃO ------------------

@app.post("/localizacao")
def salvar_localizacao(localizacao: LocalizacaoCreate, session: Session = Depends(get_session)):
    veiculo = buscar_veiculo_por_imei(session, localizacao.imei)

    if veiculo:
        localizacao.placa = veiculo.placa
        localizacao.login = veiculo.login_cliente
    else:
        localizacao.placa = f"CELULAR_{localizacao.login.upper()}"

    if not localizacao.endereco:
        localizacao.endereco = obter_endereco_real(localizacao.latitude, localizacao.longitude)

    return salvar_localizacao_db(session, localizacao)

@app.get("/ultimas_celular/{login}")
def ultima_localizacao(login: str, session: Session = Depends(get_session)):
    stmt = (
        select(Localizacao)
        .where(Localizacao.login.ilike(login))
        .order_by(Localizacao.data_hora.desc())
        .limit(1)
    )
    resultado = session.exec(stmt).first()

    if not resultado:
        return JSONResponse(content={"erro": "Nenhuma localização encontrada"}, status_code=404)

    return {
        "latitude": resultado.latitude,
        "longitude": resultado.longitude,
        "velocidade": resultado.velocidade,
        "ignicao": resultado.ignicao,
        "endereco": resultado.endereco,
        "data_hora": resultado.data_hora,
        "placa": resultado.placa
    }

@app.get("/ultimas_todos/{login}")
def ultimas_localizacoes(login: str, session: Session = Depends(get_session)):
    placa_celular = f"CELULAR_{login.upper()}"

    stmt = (
        select(Localizacao)
        .where(Localizacao.placa == placa_celular)
        .order_by(Localizacao.data_hora.desc())
        .limit(1)
    )
    ultima = session.exec(stmt).first()

    if not ultima:
        return JSONResponse(content={"erro": "Nenhuma localização encontrada"}, status_code=404)

    return [{
        "placa": ultima.placa,
        "latitude": ultima.latitude,
        "longitude": ultima.longitude,
        "velocidade": ultima.velocidade,
        "ignicao": ultima.ignicao,
        "endereco": ultima.endereco,
        "data_hora": ultima.data_hora
    }]
