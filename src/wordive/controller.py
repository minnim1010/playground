from typing import List, Optional

from .service import WordService, WordDetailService
from .models import Word


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
