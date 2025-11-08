from common.repository.base import BaseRepository
from .models import Question, Memo, Feedback


class QuestionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Question)


class MemoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Memo)


class FeedbackRepository(BaseRepository):
    def __init__(self):
        super().__init__(Feedback)
