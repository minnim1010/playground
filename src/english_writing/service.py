import json
import os
from openai import OpenAI  # 최신 openai 라이브러리 사용
from openai.types.chat import ChatCompletion


class QuestionService:
    """
    질문 데이터를 로드하고 관리하는 서비스
    """

    def __init__(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"질문 파일 '{filepath}'을 찾을 수 없습니다.")
        self.filepath = filepath

    def load_questions(self) -> list[dict]:
        """
        JSON 파일에서 질문 목록을 로드합니다.
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            if not isinstance(questions, list) or not all(isinstance(q, dict) and 'question' in q for q in questions):
                raise ValueError("질문 파일은 'question' 키를 포함하는 객체들의 리스트여야 합니다.")
            return questions
        except json.JSONDecodeError:
            print(f"오류: '{self.filepath}' 파일이 유효한 JSON 형식이 아닙니다.")
            return []
        except Exception as e:
            print(f"질문 로드 중 오류 발생: {e}")
            return []


class FeedbackService:
    """
    OpenAI API와 통신하여 영어 답변에 대한 피드백을 생성하는 서비스
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")
        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            raise ValueError(f"OpenAI 클라이언트 초기화 실패: {e}")

    def get_feedback(self, question: str, answer: str) -> str:
        """
        주어진 질문과 답변을 바탕으로 OpenAI에 피드백을 요청합니다.
        """
        system_prompt = """
        You are an expert English teacher.
        A student was given the following question:
        "{question}"

        The student provided this answer:
        "{answer}"

        Provide a sample revision (a simple, improved version) for reference.
        Also provide the feedback in Korean, starting with a brief overall summary and then detailing the points above in bullet form.
        
        Please provide constructive feedback on the student's answer.
        Focus on:
        1.  **Grammar:** Correct any grammatical errors per sentence.
        2.  **Vocabulary:** Suggest more appropriate or advanced vocabulary.
        3.  **Clarity & Flow:** Comment on the clarity and naturalness of the writing.
        4.  **Relevance:** Assess if the answer directly addresses the question.
        """

        formatted_prompt = system_prompt.format(question=question, answer=answer)

        try:
            response: ChatCompletion = self.client.chat.completions.create(
                model="gpt-5-nano",  # 또는 "gpt-4"
                messages=[
                    {"role": "system", "content": "You are a helpful assistant acting as an English teacher."},
                    {"role": "user", "content": formatted_prompt}
                ],
            )

            feedback = response.choices[0].message.content
            if feedback:
                return feedback.strip()
            else:
                return "OpenAI로부터 유효한 피드백을 받지 못했습니다."

        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생: {e}")
            return f"피드백 생성 중 오류가 발생했습니다: {e}"
