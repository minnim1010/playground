import streamlit as st
import os
from dotenv import load_dotenv

from english_writing.controller import AppController
from english_writing.service import QuestionService, FeedbackService

load_dotenv()


# --- 1. 초기화 ---
def initialize_services() -> AppController:
    """
    서비스와 컨트롤러를 초기화합니다.
    """
    try:
        question_service = QuestionService(filepath="storage/questions.json")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OPENAI_API_KEY 환경 변수를 설정해주세요.")
            st.stop()

        feedback_service = FeedbackService(api_key=api_key)
        controller = AppController(
            question_service=question_service, feedback_service=feedback_service
        )
        return controller
    except FileNotFoundError as e:
        st.error(f"초기화 오류: {e}. 'questions.json' 파일이 있는지 확인하세요.")
        st.stop()
    except ValueError as e:
        st.error(f"API 키 오류: {e}")
        st.stop()
    except Exception as e:
        st.error(f"알 수 없는 오류 발생: {e}")
        st.stop()


# --- 2. Streamlit 세션 상태 관리 ---
if "controller" not in st.session_state:
    st.session_state.controller = initialize_services()

if "question" not in st.session_state:
    st.session_state.question = st.session_state.controller.get_question()

if "past_feedbacks" not in st.session_state:
    st.session_state.past_feedbacks = []

# --- 3. UI 렌더링 ---
st.set_page_config(page_title="AI English Writing", layout="wide")

# CSS for sticky and scrollable column
st.markdown(
    """
    <style>
        /* 오른쪽 history_col (두 번째 column) 내부 스크롤 */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"] {
             max-height: 80vh;          /* 세로 최대 높이 제한 */
             overflow-y: auto;          /* 스크롤 활성화 */
             padding-right: 8px;        /* 스크롤바 공간 확보 */
         }

         /* 스크롤 시 내부 배경 색 유지 */
         div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"]::-webkit-scrollbar {
             width: 8px;
         }
         div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb {
             border-radius: 4px;
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📝 AI 영어 피드백 앱")

# 컨트롤러 가져오기
controller: AppController = st.session_state.controller


@st.fragment(run_every=180)
def display_memo_fragment():
    memo = controller.get_random_memo()
    if memo:
        st.info(memo)


# --- 화면 레이아웃 ---
main_col, history_col = st.columns([1, 1])

with main_col:
    if not st.session_state.question:
        st.error(
            "'questions.json'에서 질문을 불러오지 못했습니다. 파일을 확인해주세요."
        )
    else:
        current_question = st.session_state.question["question"]

        st.subheader("질문")
        st.info(current_question)

        user_answer = st.text_area(
            "여기에 영어 답변을 작성하세요:", height=200, key="answer"
        )

        display_memo_fragment()

        if st.button("제출 및 피드백 받기", type="primary"):
            if not user_answer.strip():
                st.warning("답변을 먼저 작성해주세요.")
            else:
                with st.spinner("AI가 피드백을 생성 중입니다... 잠시만 기다려주세요."):
                    feedback = controller.process_answer_and_get_feedback(
                        current_question, user_answer
                    )
                    st.session_state.past_feedbacks.insert(0, feedback)
                    st.rerun()

with history_col:
    if st.session_state.past_feedbacks:
        st.subheader("피드백 기록")
        for i, feedback_item in enumerate(st.session_state.past_feedbacks):
            with st.expander(
                f"기록 #{len(st.session_state.past_feedbacks) - i}", expanded=i == 0
            ):
                st.markdown(feedback_item)
