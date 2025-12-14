from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, Column, Text


class Word(SQLModel, table=True):
    __tablename__ = "wordive_words"

    id: Optional[int] = Field(default=None, primary_key=True)
    word: str = Field(unique=True, index=True)

    usages: List["WordUsage"] = Relationship(
        back_populates="word", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class WordUsage(SQLModel, table=True):
    __tablename__ = "wordive_word_usages"

    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: Optional[int] = Field(default=None, foreign_key="wordive_words.id")
    usage_type: str
    description: Optional[str] = Field(default=None, sa_column=Column(Text))

    word: Optional[Word] = Relationship(back_populates="usages")
    examples: List["ExampleSentence"] = Relationship(
        back_populates="word_usage",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    writing_practices: List["WritingPractice"] = Relationship(
        back_populates="word_usage",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ExampleSentence(SQLModel, table=True):
    __tablename__ = "wordive_example_sentences"

    id: Optional[int] = Field(default=None, primary_key=True)
    word_usage_id: Optional[int] = Field(
        default=None, foreign_key="wordive_word_usages.id"
    )
    english_sentence: str = Field(sa_column=Column(Text))
    korean_sentence: str = Field(sa_column=Column(Text))

    word_usage: Optional[WordUsage] = Relationship(back_populates="examples")


class WritingPractice(SQLModel, table=True):
    __tablename__ = "wordive_writing_practices"

    id: Optional[int] = Field(default=None, primary_key=True)
    word_usage_id: Optional[int] = Field(
        default=None, foreign_key="wordive_word_usages.id"
    )
    korean_sentence: str = Field(sa_column=Column(Text))
    english_answer: str = Field(sa_column=Column(Text))

    word_usage: Optional[WordUsage] = Relationship(back_populates="writing_practices")
    attempts: List["UserAttempt"] = Relationship(
        back_populates="writing_practice",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class UserAttempt(SQLModel, table=True):
    __tablename__ = "wordive_user_attempts"

    id: Optional[int] = Field(default=None, primary_key=True)
    writing_practice_id: Optional[int] = Field(
        default=None, foreign_key="wordive_writing_practices.id"
    )
    user_answer: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    writing_practice: Optional[WritingPractice] = Relationship(
        back_populates="attempts"
    )
