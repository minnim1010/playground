import random
from typing import Optional

from .repository import MemoRepository, FeedbackRepository
from .service import QuestionService, FeedbackService


class AppController:
    def __init__(
        self,
        question_service: QuestionService,
        feedback_service: Optional[FeedbackService] = None,
    ):
        self.question_service = question_service
        self.feedback_service = feedback_service
        self.memo_repository = MemoRepository()
        self.feedback_repository = FeedbackRepository()
        self._questions = []
        self._memos = []

    def get_question(self) -> dict | None:
        if not self._questions:
            loaded_questions = self.question_service.load_questions()
            if loaded_questions:
                self._questions = random.choice(loaded_questions)
            else:
                self._questions = None

        return self._questions

    def get_random_memo(self) -> str | None:
        if not self._memos:
            self._memos = self.memo_repository.get_all()

        if self._memos:
            return random.choice(self._memos).memo
        return None

    def process_answer_and_get_feedback(self, question: str, answer: str) -> str | None:
        if not self.feedback_service:
            print("Error: FeedbackService is not configured.")
            return "Please configure the feedback service."

        if not answer or not answer.strip():
            return "Answer is empty. Please write an answer."

        try:
            feedback = self.feedback_service.get_feedback(question, answer)
            self._save_feedback(question, answer, feedback)
            return feedback
        except Exception as e:
            print(f"Error processing feedback in controller: {e}")
            return f"An error occurred while generating feedback: {e}"

    def _save_feedback(self, question: str, answer: str, feedback: str):
        try:
            self.feedback_repository.create(
                question=question, answer=answer, feedback=feedback
            )
        except Exception as e:
            print(f"Error saving feedback: {e}")
