from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel

DB_FILE = "playground.db"
engine = create_engine(f"sqlite:///{DB_FILE}", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    SQLModel.metadata.create_all(engine)
