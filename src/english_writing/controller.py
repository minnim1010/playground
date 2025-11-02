import random
from datetime import datetime

from .service import QuestionService, FeedbackService
from typing import Optional
import json


class AppController:
    def __init__(
        self,
        question_service: QuestionService,
        feedback_service: Optional[FeedbackService] = None,
    ):
        self.question_service = question_service
        self.feedback_service = feedback_service
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
            self._memos = self._load_memos("memo.json")

        if self._memos:
            return random.choice(self._memos)["memo"]
        return None

    def _load_memos(self, filepath: str) -> list:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def process_answer_and_get_feedback(self, question: str, answer: str) -> str | None:
        if not self.feedback_service:
            print("오류: FeedbackService가 설정되지 않았습니다.")
            return "피드백 서비스를 설정해주세요."

        if not answer or not answer.strip():
            return "답변이 비어있습니다. 답변을 작성해주세요."

        try:
            feedback = self.feedback_service.get_feedback(question, answer)
            self._save_feedback(question, answer, feedback)
            return feedback
        except Exception as e:
            print(f"컨트롤러에서 피드백 처리 중 오류: {e}")
            return f"피드백 생성 중 오류가 발생했습니다: {e}"

    def _save_feedback(self, question: str, answer: str, feedback: str):
        try:
            with open("storage/private/feedback_history.json", "r+") as f:
                history = json.load(f)
                history.append(
                    {
                        "question": question,
                        "answer": answer,
                        "feedback": feedback,
                        "timestamp": str(datetime.now()),
                    }
                )
                f.seek(0)
                json.dump(history, f, indent=4)
        except (FileNotFoundError, json.JSONDecodeError):
            with open("storage/private/feedback_history.json", "w") as f:
                json.dump(
                    [
                        {
                            "question": question,
                            "answer": answer,
                            "feedback": feedback,
                            "timestamp": str(datetime.now()),
                        }
                    ],
                    f,
                    indent=4,
                )
