import os

import streamlit as st

from english_writing.controller import AppController
from english_writing.repository import FeedbackRepository
from english_writing.service import QuestionService, FeedbackService


# --- 1. Initialization ---
def initialize_services() -> AppController:
    """
    Initializes services and the main application controller.
    """
    try:
        # The QuestionService now reads from the database, no filepath needed.
        question_service = QuestionService()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OPENAI_API_KEY environment variable is not set.")
            st.stop()

        feedback_service = FeedbackService(api_key=api_key)
        controller = AppController(
            question_service=question_service, feedback_service=feedback_service
        )
        return controller
    except ValueError as e:
        st.error(f"API Key Error: {e}")
        st.stop()
    except Exception as e:
        st.error(f"An unknown error occurred during initialization: {e}")
        st.stop()


# --- 2. Streamlit Session State Management ---
if "controller" not in st.session_state:
    st.session_state.controller = initialize_services()

if "question" not in st.session_state:
    st.session_state.question = st.session_state.controller.get_question()

# Load feedback history from the database
if "past_feedbacks" not in st.session_state:
    feedback_repo = FeedbackRepository()
    # Fetch all feedback records and sort by most recent
    history = feedback_repo.get_all()
    sorted_history = sorted(history, key=lambda x: x.timestamp, reverse=True)
    st.session_state.past_feedbacks = [item.feedback for item in sorted_history]

# --- 3. UI Rendering ---
st.set_page_config(page_title="AI English Writing", layout="wide")

# CSS for sticky and scrollable column
st.markdown(
    """
    <style>
        /* Make the second column scrollable */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"] {
             max-height: 80vh;
             overflow-y: auto;
             padding-right: 8px;
         }
         /* Scrollbar styling */
         div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"]::-webkit-scrollbar {
             width: 8px;
         }
         div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb {
             border-radius: 4px;
         }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📝 AI English Feedback App")

# Get controller from session state
controller: AppController = st.session_state.controller


@st.fragment(run_every=180)
def display_memo_fragment():
    memo = controller.get_random_memo()
    if memo:
        st.info(memo)


# --- Screen Layout ---
main_col, history_col = st.columns([1, 1])

with main_col:
    if not st.session_state.question:
        st.error(
            "Could not load a question from the database. Please ensure questions are populated."
        )
    else:
        current_question = st.session_state.question["question"]

        st.subheader("Question")
        st.info(current_question)

        user_answer = st.text_area(
            "Write your English answer here:", height=200, key="answer"
        )

        display_memo_fragment()

        if st.button("Submit and Get Feedback", type="primary"):
            if not user_answer.strip():
                st.warning("Please write an answer first.")
            else:
                with st.spinner("AI is generating feedback... Please wait."):
                    feedback = controller.process_answer_and_get_feedback(
                        current_question, user_answer
                    )
                    # Add new feedback to the top of the list and rerun
                    if feedback:
                        st.session_state.past_feedbacks.insert(0, feedback)
                    st.rerun()

with history_col:
    if st.session_state.past_feedbacks:
        st.subheader("Feedback History")
        for i, feedback_item in enumerate(st.session_state.past_feedbacks):
            # Show the latest feedback expanded by default
            with st.expander(
                f"Record #{len(st.session_state.past_feedbacks) - i}", expanded=i == 0
            ):
                st.markdown(feedback_item)
