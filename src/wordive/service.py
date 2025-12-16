import json
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


class WordImportService:
    def __init__(self):
        self.word_repository = WordRepository()
        self.usage_repository = WordUsageRepository()
        self.example_repository = ExampleSentenceRepository()
        self.practice_repository = WritingPracticeRepository()

    def import_word_from_json(self, json_data: str) -> Word:
        """Parse JSON and create word with all related data."""
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        word_text = data.get("word")
        if not word_text:
            raise ValueError("JSON must contain a 'word' field")

        # Check if word already exists
        with Session(engine) as session:
            existing_word = session.exec(
                select(Word).where(Word.word == word_text)
            ).first()
            if existing_word:
                raise ValueError(f"Word '{word_text}' already exists")

        # Create word
        word = self.word_repository.create(word=word_text)

        # Process usages
        usages_data = data.get("usages", [])
        for usage_data in usages_data:
            usage_type = usage_data.get("usage_type", "")
            description = usage_data.get("description")

            # Create usage
            usage = self.usage_repository.create(
                word_id=word.id,
                usage_type=usage_type,
                description=description,
            )

            # Create examples
            examples_data = usage_data.get("examples", [])
            for example_data in examples_data:
                self.example_repository.create(
                    word_usage_id=usage.id,
                    english_sentence=example_data.get("english_sentence", ""),
                    korean_sentence=example_data.get("korean_sentence", ""),
                )

            # Create writing practices
            practices_data = usage_data.get("writing_practices", [])
            for practice_data in practices_data:
                self.practice_repository.create(
                    word_usage_id=usage.id,
                    korean_sentence=practice_data.get("korean_sentence", ""),
                    english_answer=practice_data.get("english_answer", ""),
                )

        return word
