import os
import sys
from getpass import getpass
from service import QuestionService, FeedbackService
from controller import AppController


def main():
    print("--- CLI 영어 공부 앱 ---")

    # 1. API 키 설정
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        api_key = getpass("OpenAI API 키를 입력하세요: ")

    if not api_key:
        print("API 키 없이 프로그램을 종료합니다.")
        sys.exit(1)

    # 2. 서비스 및 컨트롤러 초기화
    try:
        question_service = QuestionService(filepath="questions.json")
        feedback_service = FeedbackService(api_key=api_key)
        controller = AppController(question_service, feedback_service)
    except FileNotFoundError as e:
        print(f"오류: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"오류: {e}")
        sys.exit(1)

    # 3. 질문 로드
    questions = controller.get_questions()
    if not questions:
        print("질문을 불러오지 못했습니다. 프로그램을 종료합니다.")
        sys.exit(1)

    print(f"총 {len(questions)}개의 질문이 로드되었습니다.\n")

    # 4. 메인 루프
    try:
        for i, q_data in enumerate(questions):
            question = q_data['question']
            print("---------------------------------")
            print(f"질문 {i + 1} / {len(questions)}")
            print(f"Q: {question}")

            print("\n(답변을 여러 줄로 작성하세요. 작성이 끝나면 Enter 후 Ctrl+D (Unix) 또는 Ctrl+Z+Enter (Windows)를 누르세요.)")
            lines = []
            while True:
                try:
                    line = input("> ")
                    lines.append(line)
                except EOFError:
                    break

            answer = "\n".join(lines)

            if not answer.strip():
                print("답변이 비어있어 다음 질문으로 넘어갑니다.")
                continue

            print("\n... AI에게 피드백을 요청합니다 ...\n")

            feedback = controller.process_answer_and_get_feedback(question, answer)

            print("--- 🤖 AI 피드백 ---")
            print(feedback)
            print("---------------------------------")

            input("\n다음 질문으로 가려면 Enter를 누르세요...")

        print("모든 질문을 완료했습니다! 수고하셨습니다.")

    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        sys.exit(0)


if __name__ == "__main__":
    main()
