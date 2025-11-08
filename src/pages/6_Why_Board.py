import streamlit as st
import os
from why_board import controller


def show():
    st.set_page_config(page_title="WhyBoard", layout="wide")
    st.title("🤔 WhyBoard")

    # --- Dialog for adding a new task ---
    if st.session_state.get("show_add_dialog", False):

        @st.dialog("Add a new task")
        def add_task_dialog():
            with st.form("new_task_form"):
                title = st.text_input("Title")
                description = st.text_area("Description")
                why = st.text_area("Why is this task important?")
                how = st.text_area("How will I approach this?")
                caution = st.text_area("What are the potential risks?")

                submitted = st.form_submit_button("Add Task")
                if submitted:
                    if title:
                        controller.add_task(title, description, why, how, caution)
                        st.session_state.show_add_dialog = False
                        st.rerun()
                    else:
                        st.error("Title is required.")

        add_task_dialog()

    # --- Initialize session state for selected task ---
    if "selected_task_id" not in st.session_state:
        st.session_state.selected_task_id = None
        if st.session_state.tasks:
            st.session_state.selected_task_id = st.session_state.tasks[-1]["id"]

    # --- Layout ---
    left_col, right_col = st.columns([1, 2])

    # --- Left Section: Task List ---
    with left_col:
        st.header("Tasks")
        if st.button("＋ Add Task", use_container_width=True):
            st.session_state.show_add_dialog = True
            st.rerun()

        st.divider()

        for task in reversed(st.session_state.tasks):
            if st.button(
                task["title"], key=f"task_btn_{task['id']}", use_container_width=True
            ):
                st.session_state.selected_task_id = task["id"]
                st.rerun()

    # --- Right Section: Task Details ---
    with right_col:
        st.header("Details")

        if st.session_state.selected_task_id is None:
            st.info("Select a task to see the details, or add a new one.")
        else:
            selected_task = next(
                (
                    task
                    for task in st.session_state.tasks
                    if task["id"] == st.session_state.selected_task_id
                ),
                None,
            )

            if selected_task:
                st.subheader(selected_task["title"])
                st.text_area("Description", value=selected_task.get("description", ""))
                st.text_area("Why", value=selected_task.get("why", ""))
                st.text_area("How", value=selected_task.get("how", ""))
                st.text_area("Caution", value=selected_task.get("caution", ""))

                st.divider()

                if st.button("Get AI Suggestion", key=f"ai_btn_{selected_task['id']}"):
                    with st.spinner("Generating AI suggestion..."):
                        controller.suggest_questions_by_ai(selected_task)
                        st.rerun()

                # --- AI Response History ---
                ai_responses = controller.get_ai_responses_for_task(selected_task["id"])
                if ai_responses:
                    st.subheader("AI Suggestion History")
                    for i, response in enumerate(ai_responses):
                        with st.expander(
                            f"Suggestion {len(ai_responses) - i} ({response.get('created_at', 'No timestamp')})"
                        ):
                            st.info(response["ai_response"])
            else:
                st.warning("Selected task not found.")
                st.session_state.selected_task_id = None
                st.rerun()


if __name__ == "__main__":
    st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")
    if not st.session_state.openai_api_key:
        st.warning(
            "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
        )

    controller.initialize_session_state()
    show()
