import random
from service import QuestionService, FeedbackService
from typing import Optional


class AppController:
    def __init__(self, question_service: QuestionService, feedback_service: Optional[FeedbackService] = None):
        self.question_service = question_service
        self.feedback_service = feedback_service
        self._questions = []

    def get_questions(self) -> list[dict]:
        if not self._questions:
            loaded_questions = self.question_service.load_questions()
            if loaded_questions:
                random_question = random.choice(loaded_questions)
                self._questions = [random_question]
            else:
                self._questions = []

        return self._questions

    def process_answer_and_get_feedback(self, question: str, answer: str) -> (str | None):
        if not self.feedback_service:
            print("오류: FeedbackService가 설정되지 않았습니다.")
            return "피드백 서비스를 설정해주세요."

        if not answer or not answer.strip():
            return "답변이 비어있습니다. 답변을 작성해주세요."

        try:
            feedback = self.feedback_service.get_feedback(question, answer)
            return feedback
        except Exception as e:
            print(f"컨트롤러에서 피드백 처리 중 오류: {e}")
            return f"피드백 생성 중 오류가 발생했습니다: {e}"
