from typing import Sequence

from sqlmodel import Session, select
from database import engine
from .models import Task, AIResponse
from common.repository.base import BaseRepository


class TaskRepository(BaseRepository):
    def __init__(self):
        super().__init__(Task)

    def add(self, title, description, why, how, caution):
        return self.create(
            title=title, description=description, why=why, how=how, caution=caution
        )

    def get_all_tasks(self):
        with Session(engine) as session:
            statement = select(self.model).order_by(self.model.created_at)
            return session.exec(statement).all()


class AIResponseRepository(BaseRepository):
    def __init__(self):
        super().__init__(AIResponse)

    def add(self, task_id, response):
        self.create(task_id=task_id, ai_response=response)

    def get_for_task(self, task_id) -> Sequence[AIResponse]:
        with Session(engine) as session:
            statement = (
                select(self.model)
                .where(self.model.task_id == task_id)
                .order_by(self.model.created_at.desc())
            )
            return session.exec(statement).all()


task_repo = TaskRepository()
ai_response_repo = AIResponseRepository()
