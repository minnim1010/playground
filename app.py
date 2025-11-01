import streamlit as st
from service import QuestionService, FeedbackService
from controller import AppController


# --- 1. 초기화 ---
def initialize_services() -> AppController:
    """
    서비스와 컨트롤러를 초기화합니다.
    """
    try:
        question_service = QuestionService(filepath="questions.json")
        # FeedbackService는 API 키가 입력된 후에 초기화됩니다.
        controller = AppController(question_service=question_service)
        return controller
    except FileNotFoundError as e:
        st.error(f"초기화 오류: {e}. 'questions.json' 파일이 있는지 확인하세요.")
        st.stop()
    except Exception as e:
        st.error(f"알 수 없는 오류 발생: {e}")
        st.stop()


# --- 2. Streamlit 세션 상태 관리 ---
if 'controller' not in st.session_state:
    st.session_state.controller = initialize_services()

if 'questions' not in st.session_state:
    st.session_state.questions = st.session_state.controller.get_questions()

if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0

if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

# --- 3. UI 렌더링 ---
st.set_page_config(page_title="영어 공부 앱", layout="wide")
st.title("📝 AI 영어 피드백 앱")

# 컨트롤러 가져오기
controller: AppController = st.session_state.controller

# --- 사이드바: API 키 입력 ---
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("OpenAI API Key", type="password")

    if api_key:
        try:
            feedback_service = FeedbackService(api_key=api_key)
            controller.set_feedback_service(feedback_service)
            st.success("API 키가 설정되었습니다!", icon="✅")
        except ValueError as e:
            st.error(f"API 키 오류: {e}")
    else:
        st.warning("OpenAI API 키를 입력해주세요.", icon="⚠️")

# --- 메인 화면 ---
if not st.session_state.questions:
    st.error("'questions.json'에서 질문을 불러오지 못했습니다. 파일을 확인해주세요.")
else:
    # --- 질문 표시 ---
    total_questions = len(st.session_state.questions)
    idx = st.session_state.current_question_index
    current_q_data = st.session_state.questions[idx]
    current_question = current_q_data['question']

    st.subheader(f"질문 {idx + 1} / {total_questions}")
    st.info(current_question)

    # --- 답변 입력 ---
    # key를 사용하여 질문이 바뀔 때마다 text_area를 고유하게 만듭니다.
    user_answer = st.text_area("여기에 영어 답변을 작성하세요:", height=200, key=f"answer_{idx}")

    # --- 버튼 ---
    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        if st.button("⬅️ 이전 질문"):
            st.session_state.current_question_index = (idx - 1) % total_questions
            st.session_state.feedback = ""  # 피드백 초기화
            st.rerun()

    with col2:
        if st.button("다음 질문 ➡️"):
            st.session_state.current_question_index = (idx + 1) % total_questions
            st.session_state.feedback = ""  # 피드백 초기화
            st.rerun()

    with col3:
        if st.button("제출 및 피드백 받기", type="primary", disabled=(not api_key)):
            if not controller.feedback_service:
                st.error("OpenAI API 키를 먼저 입력해주세요.")
            elif not user_answer.strip():
                st.warning("답변을 먼저 작성해주세요.")
            else:
                with st.spinner("AI가 피드백을 생성 중입니다... 잠시만 기다려주세요."):
                    feedback = controller.process_answer_and_get_feedback(
                        current_question,
                        user_answer
                    )
                    st.session_state.feedback = feedback

    # --- 피드백 표시 ---
    if st.session_state.feedback:
        st.divider()
        st.subheader("🤖 AI 피드백")
        st.markdown(st.session_state.feedback)
