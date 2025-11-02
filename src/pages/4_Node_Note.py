import streamlit as st
from node_note import controller

# --- Main Application UI ---


def main():
    """
    The main function that runs the Streamlit application UI.
    """
    st.set_page_config(page_title="Node Note", layout="wide")
    st.title("🌳 Node Note")
    st.caption(
        "Structure your thoughts in a tree. Create topics, add logs, and promote logs to new topics."
    )

    # Load all topics and logs using the controller
    topics = controller.get_all_topics()

    # Initialize session state for the current topic
    if "current_topic_id" not in st.session_state:
        root_topic = next((t for t in topics if t["parent_topic_id"] is None), None)
        st.session_state.current_topic_id = root_topic["id"] if root_topic else None

    # Initialize session state for log sorting
    if "log_sort_desc" not in st.session_state:
        st.session_state.log_sort_desc = False  # Default to oldest first

    # Initialize session state for file upload
    if "last_uploaded_file_id" not in st.session_state:
        st.session_state.last_uploaded_file_id = None
    if "show_image_uploader" not in st.session_state:
        st.session_state.show_image_uploader = False

    # --- Page Layout ---
    left_column, right_column = st.columns([1, 3])

    # --- Left Column for Topic Navigation and Creation ---
    with left_column:
        # Topic Search
        search_term = st.text_input("Search Topics", key="search_topics")

        # New Topic Creation
        with st.expander("➕ New Topic"):
            new_topic_title = st.text_input(
                "Enter new topic title", key="new_topic_title_main"
            )
            if st.button("Create Topic"):
                if new_topic_title and st.session_state.current_topic_id:
                    new_topic = controller.create_topic(
                        new_topic_title, st.session_state.current_topic_id
                    )
                    st.session_state.current_topic_id = new_topic["id"]
                    st.rerun()
                else:
                    st.warning("Topic title cannot be empty.")

        # Topic List Display
        st.subheader("All Topics")
        filtered_topics = topics
        if search_term:
            filtered_topics = [
                t for t in topics if search_term.lower() in t["title"].lower()
            ]

        for topic in sorted(
            filtered_topics, key=lambda x: x["created_at"], reverse=True
        ):
            if st.button(topic["title"], key=f"topic_btn_{topic['id']}"):
                st.session_state.current_topic_id = topic["id"]
                st.rerun()

    # --- Right Column for Logs and Graph ---
    with right_column:
        current_topic = next(
            (t for t in topics if t["id"] == st.session_state.current_topic_id), None
        )

        if not current_topic:
            st.error(
                "Selected topic not found. Please select a topic from the navigator."
            )
            return

        st.header(f"📜 {current_topic['title']}")

        # Log Input Form
        log_text = st.text_input(
            "Add a one-line log...", key="log_input", placeholder="What's on your mind?"
        )

        log_col, img_col = st.columns(2)
        with log_col:
            if st.button("Add Log", key="add_log_button") and log_text:
                controller.add_log(log_text, current_topic["id"])
                st.rerun()

        with img_col:
            if st.button("Add Image"):
                st.session_state.show_image_uploader = (
                    not st.session_state.show_image_uploader
                )

        # Image Upload Section
        if st.session_state.get("show_image_uploader", False):
            uploaded_file = st.file_uploader(
                "Upload an image", type=["png", "jpg", "jpeg"]
            )
            if uploaded_file is not None:
                if st.session_state.last_uploaded_file_id != uploaded_file.file_id:
                    controller.add_image_log(uploaded_file, current_topic["id"])
                    st.session_state.last_uploaded_file_id = uploaded_file.file_id
                    st.session_state.show_image_uploader = False
                    st.rerun()

        # Display Logs for the Current Topic
        st.subheader("Recent Logs")

        # Sort button
        sort_order_label = (
            "Newest First" if st.session_state.log_sort_desc else "Oldest First"
        )
        if st.button(f"Sort by: {sort_order_label}"):
            st.session_state.log_sort_desc = not st.session_state.log_sort_desc
            st.rerun()

        current_logs = controller.get_logs_for_topic(current_topic["id"])
        for log in sorted(
            current_logs,
            key=lambda x: x["created_at"],
            reverse=st.session_state.log_sort_desc,
        ):
            log_type = log.get("type", "text")
            if log_type == "image":
                st.image(log["text"], use_container_width=True)
            else:  # text log
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"- {log['text']}")
                with col2:
                    if not log.get("is_promoted"):
                        if st.button(
                            "↗️",
                            key=f"promote_{log['id']}",
                            help="Create a new topic from this log",
                        ):
                            new_topic = controller.promote_log_to_topic(
                                log, current_topic["id"]
                            )
                            if new_topic:
                                st.session_state.current_topic_id = new_topic["id"]
                                st.success(
                                    f"Promoted to new topic: '{new_topic['title']}'"
                                )
                                st.rerun()
                    else:
                        st.markdown("*(Promoted)*")


if __name__ == "__main__":
    main()
