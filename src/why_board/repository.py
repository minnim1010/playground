from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from common.repository.base import Base, BaseRepository, SessionLocal, model_to_dict


# --- ORM Models ---
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    why = Column(Text)
    how = Column(Text)
    caution = Column(Text)
    reflection = Column(Text)
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        String, nullable=False, default=lambda: datetime.now().isoformat()
    )
    responses = relationship(
        "AIResponse", back_populates="task", cascade="all, delete-orphan"
    )


class AIResponse(Base):
    __tablename__ = "ai_responses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    ai_response = Column(Text, nullable=False)
    created_at = Column(
        String, nullable=False, default=lambda: datetime.now().isoformat()
    )
    task = relationship("Task", back_populates="responses")


# --- Specific Repositories ---
class TaskRepository(BaseRepository):
    def __init__(self):
        super().__init__(Task)

    def add(self, title, description, why, how, caution):
        task = self.create(
            title=title, description=description, why=why, how=how, caution=caution
        )
        return model_to_dict(task)

    def get_all_tasks(self):
        tasks = self.get_all()
        return [
            model_to_dict(task) for task in sorted(tasks, key=lambda t: t.created_at)
        ]


class AIResponseRepository(BaseRepository):
    def __init__(self):
        super().__init__(AIResponse)

    def add(self, task_id, response):
        self.create(task_id=task_id, ai_response=response)

    def get_for_task(self, task_id):
        db = SessionLocal()
        responses = (
            db.query(self.model)
            .filter(self.model.task_id == task_id)
            .order_by(self.model.created_at.desc())
            .all()
        )
        db.close()
        return [model_to_dict(resp) for resp in responses]


# --- Repository Instances ---
task_repo = TaskRepository()
ai_response_repo = AIResponseRepository()
