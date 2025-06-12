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
from models import Localizacao, Veiculo, CoordenadaCache
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
criar_banco()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/mapa.html")
def abrir_mapa():
    return FileResponse("static/mapa.html")

# CLIENTE

@app.post("/registrar")
def registrar(cliente: ClienteCreate, session: Session = Depends(get_session)):
    return criar_cliente(session, cliente)

@app.get("/cliente/{login}")
def obter_cliente(login: str, session: Session = Depends(get_session)):
    return buscar_cliente_por_login(session, login)

# VEÍCULO

@app.post("/cadastrar_veiculo")
def cadastrar_veiculo(veiculo: VeiculoCreate, session: Session = Depends(get_session)):
    return criar_veiculo(session, veiculo)

@app.get("/veiculos/{login}")
def veiculos_cliente(login: str, session: Session = Depends(get_session)):
    login = login.strip().lower()
    stmt = select(Veiculo).where(Veiculo.login_cliente.ilike(login))
    return session.exec(stmt).all()

# GEOLOCALIZAÇÃO COM CACHE

def obter_endereco_real(lat: float, lon: float, session: Session) -> str:
    lat_str = f"{lat:.5f}"
    lon_str = f"{lon:.5f}"

    # Verificar se já está no cache
    cache_stmt = select(CoordenadaCache).where(
        CoordenadaCache.lat == lat_str, CoordenadaCache.lon == lon_str
    )
    cache_result = session.exec(cache_stmt).first()
    if cache_result:
        return cache_result.endereco

    try:
        api_key = os.getenv("LOCATIONIQ_API_KEY")
        if not api_key:
            return "Chave da API LocationIQ não configurada"

        url = f"https://us1.locationiq.com/v1/reverse.php?key={api_key}&lat={lat}&lon={lon}&format=json"
        resposta = requests.get(url, timeout=10)
        if resposta.status_code == 200:
            dados = resposta.json()
            endereco = dados.get("display_name", "Endereço não encontrado")

            # Salvar no cache
            novo_cache = CoordenadaCache(lat=lat_str, lon=lon_str, endereco=endereco)
            session.add(novo_cache)
            session.commit()

            return endereco
        else:
            return "Endereço não encontrado"
    except Exception:
        return "Erro ao obter endereço"

# LOCALIZAÇÃO

@app.post("/localizacao")
def salvar_localizacao(localizacao: LocalizacaoCreate, session: Session = Depends(get_session)):
    veiculo = buscar_veiculo_por_imei(session, localizacao.imei)

    if veiculo:
        localizacao.placa = veiculo.placa
        localizacao.login = veiculo.login_cliente
    else:
        localizacao.placa = f"CELULAR_{localizacao.login.upper()}"

    if not localizacao.endereco:
        localizacao.endereco = obter_endereco_real(localizacao.latitude, localizacao.longitude, session)

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
