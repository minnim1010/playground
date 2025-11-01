import streamlit as st
import os
import datetime
import pandas as pd
from dotenv import load_dotenv
from ai_scheduler.service import AISchedulerService
from ai_scheduler.controller import AISchedulerController

# --- 1. Initialization & Controller Setup --- #
load_dotenv()
st.set_page_config(page_title="AI To-Do Scheduler", page_icon="🤖", layout="wide")


@st.cache_resource
def initialize_scheduler_controller() -> AISchedulerController:
    api_key = os.getenv("OPENAI_API_KEY")
    try:
        service = AISchedulerService(api_key=api_key)
        return AISchedulerController(service)
    except Exception as e:
        st.error(f"Initialization error: {e}")
        st.stop()


controller: AISchedulerController = initialize_scheduler_controller()

# --- 2. Session State Management --- #
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "selected_task_id" not in st.session_state:
    st.session_state.selected_task_id = None


# --- 3. Dialog (Modal) Definition --- #
@st.dialog("Task Management")
def task_dialog(task_id=None):
    is_edit_mode = task_id is not None
    if is_edit_mode:
        task = controller.get_task_by_id(task_id)
        if not task:
            st.error("Task not found.")
            return
    else:
        task = {}

    st.write("**New Task**" if not is_edit_mode else "**Edit Task**")
    name = st.text_input("Task", value=task.get("name", ""))
    description = st.text_area("Description", value=task.get("description", ""))
    deadline = st.date_input(
        "Deadline", value=task.get("deadline", datetime.date.today())
    )
    duration = st.number_input(
        "Estimated time (hours)", min_value=1, value=task.get("duration", 1)
    )
    urgent = st.checkbox("Urgent", value=task.get("urgent", False))
    completed = (
        st.checkbox("Completed", value=task.get("completed", False))
        if is_edit_mode
        else False
    )

    if st.button("Save"):
        if not name:
            st.warning("Please enter a task name.")
            return
        if is_edit_mode:
            controller.update_task(
                task_id, name, deadline, duration, urgent, completed, description
            )
        else:
            controller.add_task(name, deadline, duration, urgent, description)
        st.rerun()


# --- 4. Main UI Rendering --- #
st.title("🤖 AI To-Do Scheduler")

# --- Display To-Do List (DataFrame) ---
st.subheader("📋 My To-Do List")
all_tasks = controller.get_all_tasks()
selected_task = None

if not all_tasks:
    st.info("No tasks added yet. Press the 'Add ➕' button to add a new task.")
else:
    df = pd.DataFrame(all_tasks)
    df_display = df[
        ["name", "description", "deadline", "duration", "urgent", "completed"]
    ].rename(
        columns={
            "name": "Task",
            "description": "Description",
            "deadline": "Deadline",
            "duration": "Duration(H)",
            "urgent": "Urgent",
            "completed": "Completed",
        }
    )
    df_display.insert(0, "Select", False)

    edited_df = st.data_editor(
        df_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Select": st.column_config.CheckboxColumn(required=True),
        },
        disabled=[
            "Task",
            "Description",
            "Deadline",
            "Duration(H)",
            "Urgent",
            "Completed",
        ],
    )

    selected_rows = edited_df[edited_df.Select]
    if not selected_rows.empty:
        # If user selects multiple, just take the first one.
        selected_task_name = selected_rows.iloc[0]["Task"]
        selected_task = next(
            (t for t in all_tasks if t["name"] == selected_task_name), None
        )


# --- Function Buttons --- #
btn_cols = st.columns(5)
if btn_cols[0].button("Add ➕"):
    task_dialog()

if selected_task:
    if btn_cols[1].button("Edit ✏️"):
        task_dialog(selected_task["id"])
    if btn_cols[2].button("Delete 🗑️"):
        controller.delete_task(selected_task["id"])
        st.rerun()
    if btn_cols[4].button("Get AI Recommendation", type="primary"):
        st.session_state.selected_task_id = selected_task["id"]
        st.session_state.recommendations = []  # Clear old recommendations
        with st.spinner("AI is analyzing your calendar..."):
            result = controller.find_and_recommend_time(selected_task["id"])
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.recommendations = result["recommendations"]
        st.rerun()

# --- Display Recommendation Results ---
if st.session_state.recommendations and st.session_state.selected_task_id:
    st.divider()
    selected_task_for_rec = controller.get_task_by_id(st.session_state.selected_task_id)

    if selected_task_for_rec:
        st.subheader(f"✨ AI Recommended Time: '{selected_task_for_rec['name']}'")

        for i, rec in enumerate(st.session_state.recommendations):
            start, end = rec["start"], rec["end"]
            time_str = (
                f"{start.strftime('%m/%d %A, %p %I:%M')} - {end.strftime('%p %I:%M')}"
            )

            rec_col1, rec_col2 = st.columns([3, 1])
            rec_col1.write(f"**Recommendation {i+1}:** {time_str}")
            if rec_col2.button("Confirm this time", key=f"sched_{i}"):
                with st.spinner("Registering the event to your calendar..."):
                    link = controller.schedule_event(
                        selected_task_for_rec["name"],
                        start,
                        end,
                        selected_task_for_rec.get("description", ""),
                    )
                    if link:
                        st.success(
                            f"Event successfully registered! [Check on Calendar]({link})"
                        )
                        controller.update_task(
                            selected_task_for_rec["id"],
                            selected_task_for_rec["name"],
                            selected_task_for_rec["deadline"],
                            selected_task_for_rec["duration"],
                            selected_task_for_rec["urgent"],
                            True,
                            selected_task_for_rec.get("description", ""),
                        )
                        st.session_state.recommendations = []
                        st.session_state.selected_task_id = None
                        st.rerun()
                    else:
                        st.error("Failed to register the event to the calendar.")
    else:
        # Task might have been deleted. Clear session state and rerun.
        st.session_state.recommendations = []
        st.session_state.selected_task_id = None
        st.rerun()
