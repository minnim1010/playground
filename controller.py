from service import QuestionService, FeedbackService
from typing import Optional


class AppController:
    """
    애플리케이션의 로직을 조율하는 컨트롤러
    (서비스 계층과 뷰 계층을 연결)
    """

    def __init__(self, question_service: QuestionService, feedback_service: Optional[FeedbackService] = None):
        self.question_service = question_service
        self.feedback_service = feedback_service
        self._questions = []  # 질문 캐싱

    def set_feedback_service(self, feedback_service: FeedbackService):
        """
        API 키가 나중에 제공될 경우를 대비해 피드백 서비스 설정
        """
        self.feedback_service = feedback_service

    def get_questions(self) -> list[dict]:
        """
        질문 목록을 가져옵니다 (캐시된 경우 캐시 사용).
        """
        if not self._questions:
            self._questions = self.question_service.load_questions()
        return self._questions

    def process_answer_and_get_feedback(self, question: str, answer: str) -> (str | None):
        """
        답변을 처리하고 피드백 서비스에 피드백을 요청합니다.
        """
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
