import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Database Setup ---
DB_FILE = "storage/private/why_board.db"
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Initializes the database and creates tables from models."""
    Base.metadata.create_all(bind=engine)


# --- Generic Base Repository ---
class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get(self, id: int):
        db = SessionLocal()
        obj = db.query(self.model).get(id)
        db.close()
        return obj

    def get_all(self):
        db = SessionLocal()
        objs = db.query(self.model).all()
        db.close()
        return objs

    def create(self, **kwargs):
        db = SessionLocal()
        instance = self.model(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        db.close()
        return instance

    def update(self, id: int, **kwargs):
        db = SessionLocal()
        obj = db.query(self.model).get(id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
        db.close()
        return obj


# --- Model to Dictionary Helper ---
def model_to_dict(instance):
    """Converts a SQLAlchemy model instance to a dictionary."""
    if instance is None:
        return None
    return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
