from sqlmodel import Session, select
from database import engine


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get(self, id: int):
        with Session(engine) as session:
            return session.get(self.model, id)

    def get_all(self):
        with Session(engine) as session:
            statement = select(self.model)
            return session.exec(statement).all()

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        with Session(engine) as session:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance

    def update(self, id: int, **kwargs):
        with Session(engine) as session:
            obj = session.get(self.model, id)
            if obj:
                for key, value in kwargs.items():
                    setattr(obj, key, value)
                session.add(obj)
                session.commit()
                session.refresh(obj)
            return obj
