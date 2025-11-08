from typing import Sequence

import streamlit as st

from why_board.models import AIResponse
from why_board.service import task_service, ai_response_service


def initialize_session_state():
    """
    Initializes the database and loads tasks into the session state.
    """
    if "tasks" not in st.session_state:
        st.session_state.tasks = task_service.get_all_tasks()
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""


def add_task(title, description, why, how, caution):
    """
    Adds a new task using the service and updates the session state.
    """
    new_task = task_service.add_task(title, description, why, how, caution)
    if new_task:
        st.session_state.tasks.append(new_task)
    return new_task


def get_ai_responses_for_task(task_id) -> Sequence[AIResponse]:
    """
    Retrieves all AI responses for a given task_id from the service.
    """
    return ai_response_service.get_responses_for_task(task_id)


def suggest_questions_by_ai(task):
    return ai_response_service.suggest_question_by_ai(task)


# Initialize session state when the controller is imported
initialize_session_state()
