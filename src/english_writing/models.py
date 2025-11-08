from sqlmodel import Field, SQLModel
from datetime import datetime


class Question(SQLModel, table=True):
    __tablename__ = "english_writing_question"
    id: int | None = Field(default=None, primary_key=True)
    question: str


class Memo(SQLModel, table=True):
    __tablename__ = "english_writing_memo"
    id: int | None = Field(default=None, primary_key=True)
    memo: str


class Feedback(SQLModel, table=True):
    __tablename__ = "english_writing_feedback"
    id: int | None = Field(default=None, primary_key=True)
    question_id: int | None = Field(
        default=None, foreign_key="english_writing_question.id"
    )
    answer: str
    feedback: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
