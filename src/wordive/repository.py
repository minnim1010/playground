from common.repository.base import BaseRepository
from .models import Word, WordUsage, ExampleSentence, WritingPractice, UserAttempt


class WordRepository(BaseRepository):
    def __init__(self):
        super().__init__(Word)


class WordUsageRepository(BaseRepository):
    def __init__(self):
        super().__init__(WordUsage)


class ExampleSentenceRepository(BaseRepository):
    def __init__(self):
        super().__init__(ExampleSentence)


class WritingPracticeRepository(BaseRepository):
    def __init__(self):
        super().__init__(WritingPractice)


class UserAttemptRepository(BaseRepository):
    def __init__(self):
        super().__init__(UserAttempt)
