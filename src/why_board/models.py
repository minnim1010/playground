from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, Column, Text


class Task(SQLModel, table=True):
    __tablename__ = "why_board_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    why: Optional[str] = Field(default=None, sa_column=Column(Text))
    how: Optional[str] = Field(default=None, sa_column=Column(Text))
    caution: Optional[str] = Field(default=None, sa_column=Column(Text))
    reflection: Optional[str] = Field(default=None, sa_column=Column(Text))
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    responses: List["AIResponse"] = Relationship(
        back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class AIResponse(SQLModel, table=True):
    __tablename__ = "why_board_ai_responses"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="why_board_tasks.id")
    ai_response: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    task: Optional[Task] = Relationship(back_populates="responses")
