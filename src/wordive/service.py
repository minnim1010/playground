from typing import List, Optional

from sqlmodel import Session, select
from database import engine

from .repository import (
    WordRepository,
    WordUsageRepository,
    ExampleSentenceRepository,
    WritingPracticeRepository,
    UserAttemptRepository,
)
from .models import Word, WordUsage, ExampleSentence, WritingPractice, UserAttempt


class WordService:
    def __init__(self):
        self.repository = WordRepository()

    def get_all_words(self) -> List[Word]:
        return self.repository.get_all()

    def search_words(self, query: str) -> List[Word]:
        with Session(engine) as session:
            statement = select(Word).where(Word.word.ilike(f"%{query}%"))
            return list(session.exec(statement).all())

    def get_word_by_id(self, word_id: int) -> Optional[Word]:
        return self.repository.get(word_id)


class WordDetailService:
    def __init__(self):
        self.word_repository = WordRepository()
        self.usage_repository = WordUsageRepository()
        self.example_repository = ExampleSentenceRepository()
        self.practice_repository = WritingPracticeRepository()
        self.attempt_repository = UserAttemptRepository()

    def get_word_with_details(self, word_id: int) -> Optional[Word]:
        with Session(engine) as session:
            word = session.get(Word, word_id)
            if word:
                usages = session.exec(
                    select(WordUsage).where(WordUsage.word_id == word_id)
                ).all()
                word.usages = list(usages)

                for usage in word.usages:
                    examples = session.exec(
                        select(ExampleSentence).where(
                            ExampleSentence.word_usage_id == usage.id
                        )
                    ).all()
                    usage.examples = list(examples)

                    practices = session.exec(
                        select(WritingPractice).where(
                            WritingPractice.word_usage_id == usage.id
                        )
                    ).all()
                    usage.writing_practices = list(practices)

            return word

    def save_user_attempt(
        self, writing_practice_id: int, user_answer: str
    ) -> UserAttempt:
        return self.attempt_repository.create(
            writing_practice_id=writing_practice_id, user_answer=user_answer
        )
