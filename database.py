from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega variáveis do .env

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=False  # Deixe True se quiser ver as queries no terminal
)

def criar_banco():
    SQLModel.metadata.create_all(engine)

def get_session():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
