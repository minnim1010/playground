from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel

# Import all models here to ensure they are registered with SQLModel


DB_FILE = "playground.db"
_engine = None


def get_engine():
    global _engine
    if _engine is None:
        # I've changed echo to False to disable logging.
        _engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)
        SQLModel.metadata.create_all(_engine)
    return _engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
