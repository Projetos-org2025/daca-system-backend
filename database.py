from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool

DATABASE_URL = "sqlite:///rastreador.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

def criar_banco():
    SQLModel.metadata.create_all(engine)

def get_session():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
