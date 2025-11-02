import streamlit as st
import os
from dotenv import load_dotenv
from micro_journal.service import MicroJournalService
from micro_journal.controller import MicroJournalController

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- 1. 초기화 --- #
st.set_page_config(page_title="Micro Journal", page_icon="✍️", layout="wide")


def initialize_controller() -> MicroJournalController:
    """서비스와 컨트롤러를 초기화합니다."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning(
            "OPENAI_API_KEY가 설정되지 않았습니다. 요약 기능이 제한될 수 있습니다."
        )

    db_path = "storage/private/micro_journal.json"
    service = MicroJournalService(db_path=db_path, api_key=api_key)
    controller = MicroJournalController(service)
    return controller


# 세션 상태 초기화
if "journal_controller" not in st.session_state:
    st.session_state.journal_controller = initialize_controller()
if "summary" not in st.session_state:
    st.session_state.summary = None

controller: MicroJournalController = st.session_state.journal_controller

# --- 2. UI 렌더링 --- #
st.title("✍️ Micro Journal: 하루 한 줄, 나를 돌아보는 시간")
st.markdown(
    "**하루의 생각, 배움, 느낌을 짧게 기록하고, AI가 자동으로 회고를 도와줍니다.**"
)

# --- 입력 UI ---
new_entry_content = st.text_input(
    "오늘의 기록을 남겨보세요 (예: 오늘 새로운 알고리즘을 배웠다)",
    max_chars=200,
    placeholder="여기에 입력...",
    key="new_entry_input",
)

if st.button("기록 추가하기", type="primary"):
    if new_entry_content:
        controller.add_new_entry(new_entry_content)
        st.success("기록이 성공적으로 추가되었습니다!")
        st.session_state.summary = None
        st.rerun()
    else:
        st.warning("내용을 입력해주세요.")

st.divider()

# --- 요약 및 기록 표시 --- #
summary_col, history_col = st.columns(2)

with summary_col:
    st.subheader("AI 회고 리포트")

    # 컨트롤들을 위한 컬럼 생성
    control_col1, control_col2 = st.columns([2, 1])

    with control_col1:
        summary_period = st.radio(
            "요약 기간 선택", ["주간", "월간"], horizontal=True, key="summary_period"
        )

    with control_col2:
        generate_button = st.button("AI 회고 생성하기")

    # 버튼 클릭 시 요약 생성 로직
    if generate_button:
        period = "weekly" if summary_period == "주간" else "monthly"
        with st.spinner("AI가 회고를 생성 중입니다... 잠시만 기다려주세요."):
            if period == "weekly":
                summary_text = controller.get_weekly_summary()
            else:
                summary_text = controller.get_monthly_summary()
            st.session_state.summary = summary_text

    # 요약 결과 표시 컨테이너
    with st.container(border=True, height=450):
        if st.session_state.summary:
            st.markdown(st.session_state.summary)
        else:
            st.info(
                "기간을 선택하고 'AI 회고 생성하기' 버튼을 눌러 리포트를 받아보세요."
            )

with history_col:
    st.subheader("나의 모든 기록")
    all_entries = controller.get_entries_for_display()

    if not all_entries:
        st.info("아직 기록된 내용이 없습니다. 첫 기록을 남겨보세요!")
    else:
        with st.container(height=500):
            for entry in all_entries:
                col1, col2 = st.columns([1, 4])
                with col1:
                    date_str = entry["timestamp"].split("T")[0]
                    st.caption(date_str)
                with col2:
                    st.markdown(f"- {entry['content']}")
