from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, SQLModel

# Import all models to ensure they're registered with SQLModel.metadata
# before create_all() is called

DB_FILE = "playground.db"
_engine = None


def get_engine():
    global _engine
    if _engine is None:
        # I've changed echo to False to disable logging.
        _engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)
        # Create all tables - models are imported above to ensure they're registered
        SQLModel.metadata.create_all(_engine, checkfirst=True)
    return _engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
