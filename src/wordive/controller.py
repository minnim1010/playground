from typing import List, Optional

from .service import (
    WordService,
    WordDetailService,
    WordImportService,
    WritingPracticeQuizService,
)
from .models import Word, WritingPractice


class WordListController:
    def __init__(self):
        self.word_service = WordService()

    def get_words(self, search_query: Optional[str] = None) -> List[Word]:
        if search_query:
            return self.word_service.search_words(search_query)
        return self.word_service.get_all_words()


class WordDetailController:
    def __init__(self):
        self.word_detail_service = WordDetailService()

    def get_word_details(self, word_id: int) -> Optional[Word]:
        return self.word_detail_service.get_word_with_details(word_id)

    def save_attempt(self, writing_practice_id: int, user_answer: str):
        return self.word_detail_service.save_user_attempt(
            writing_practice_id, user_answer
        )


class WordImportController:
    def __init__(self):
        self.import_service = WordImportService()

    def import_word_from_json(self, json_data: str) -> Word:
        """Import word from JSON data."""
        return self.import_service.import_word_from_json(json_data)


class WritingPracticeQuizController:
    def __init__(self):
        self.quiz_service = WritingPracticeQuizService()
        self.word_detail_service = WordDetailService()

    def get_recent_practice(self) -> Optional[WritingPractice]:
        """Get a random practice from recently studied practices."""
        recent_practices = self.quiz_service.get_recent_practices(days=7)
        if not recent_practices:
            return None
        import random

        return random.choice(recent_practices)

    def get_random_practice(self) -> Optional[WritingPractice]:
        """Get a random practice from all practices."""
        return self.quiz_service.get_random_practice()

    def save_quiz_attempt(self, writing_practice_id: int, user_answer: str):
        """Save a quiz attempt."""
        return self.word_detail_service.save_user_attempt(
            writing_practice_id, user_answer
        )
