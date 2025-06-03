from sqlmodel import Session, select
from models import Cliente, Veiculo, Localizacao
from schemas import ClienteCreate, VeiculoCreate, LocalizacaoCreate

# --- Cliente ---
def criar_cliente(session: Session, cliente: ClienteCreate) -> Cliente:
    novo = Cliente(**cliente.dict())
    session.add(novo)
    session.commit()
    session.refresh(novo)
    return novo

def buscar_cliente_por_login(session: Session, login: str) -> Cliente | None:
    return session.exec(select(Cliente).where(Cliente.login == login)).first()

# --- Veículo ---
def criar_veiculo(session: Session, veiculo: VeiculoCreate) -> Veiculo:
    novo = Veiculo(**veiculo.dict())
    session.add(novo)
    session.commit()
    session.refresh(novo)
    return novo

def buscar_veiculos_por_login(session: Session, login: str) -> list[Veiculo]:
    return session.exec(select(Veiculo).where(Veiculo.login_cliente == login.strip().lower())).all()

def buscar_veiculo_por_imei(session: Session, imei: str) -> Veiculo | None:
    return session.exec(select(Veiculo).where(Veiculo.imei == imei)).first()

# --- Localização ---
def salvar_localizacao_db(session: Session, dados: LocalizacaoCreate) -> Localizacao:
    nova = Localizacao(**dados.dict(exclude_unset=True))
    session.add(nova)
    session.commit()
    session.refresh(nova)
    return nova

def buscar_ultima_localizacao(session: Session, placa: str) -> Localizacao | None:
    return session.exec(
        select(Localizacao)
        .where(Localizacao.placa == placa)
        .order_by(Localizacao.data_hora.desc())
        .limit(1)
    ).first()
