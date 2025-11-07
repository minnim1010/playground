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

    # Initialize session state
    if "current_topic_id" not in st.session_state:
        root_topic = next((t for t in topics if t.get("parent_topic_id") is None), None)
        st.session_state.current_topic_id = root_topic["id"] if root_topic else None
    if "log_sort_desc" not in st.session_state:
        st.session_state.log_sort_desc = False
    if "show_image_uploader" not in st.session_state:
        st.session_state.show_image_uploader = False
    if "move_mode" not in st.session_state:
        st.session_state.move_mode = False
    if "logs_to_move" not in st.session_state:
        st.session_state.logs_to_move = []

    # --- Sidebar for Topic Navigation and Creation ---
    with st.sidebar:
        st.header("Topics")
        search_term = st.text_input("Search Topics", key="search_topics")

        st.subheader("All Topics")
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
        filtered_topics = (
            [t for t in topics if search_term.lower() in t["title"].lower()]
            if search_term
            else topics
        )
        for topic in sorted(
            filtered_topics, key=lambda x: x["created_at"], reverse=True
        ):
            if st.button(topic["title"], key=f"topic_btn_{topic['id']}"):
                st.session_state.current_topic_id = topic["id"]
                st.rerun()

    # --- Main Content Area for Logs ---
    current_topic = next(
        (t for t in topics if t["id"] == st.session_state.current_topic_id), None
    )
    if not current_topic:
        st.error("Selected topic not found.")
        return

    st.header(f"📜 {current_topic['title']}")

    # --- Log Input Area ---
    log_text = st.text_input(
        "Add a one-line log...", key="log_input", placeholder="What's on your mind?"
    )
    log_col, img_col = st.columns(2)
    if log_col.button("Add Log", key="add_log_button") and log_text:
        controller.add_log(log_text, current_topic["id"])
        st.rerun()
    if img_col.button("Add Image"):
        st.session_state.show_image_uploader = not st.session_state.show_image_uploader

    if st.session_state.show_image_uploader:
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            controller.add_image_log(uploaded_file, current_topic["id"])
            st.session_state.show_image_uploader = False
            st.rerun()

    st.divider()

    # --- Log Display Area ---
    st.subheader("Logs")
    sort_col, move_col = st.columns([1, 1])
    sort_order_label = (
        "Newest First" if st.session_state.log_sort_desc else "Oldest First"
    )
    if sort_col.button(f"Sort by: {sort_order_label}"):
        st.session_state.log_sort_desc = not st.session_state.log_sort_desc
        st.rerun()

    if move_col.button("Move Logs"):
        st.session_state.move_mode = not st.session_state.move_mode
        st.session_state.logs_to_move = []  # Reset selection on mode change
        st.rerun()

    # --- Display Logs ---
    current_logs = controller.get_logs_for_topic(current_topic["id"])
    sorted_logs = sorted(
        current_logs,
        key=lambda x: x["created_at"],
        reverse=st.session_state.log_sort_desc,
    )

    for log in sorted_logs:
        cols = (
            st.columns([1, 10, 2])
            if st.session_state.move_mode
            else st.columns([10, 2])
        )

        if st.session_state.move_mode:
            checked = cols[0].checkbox(
                "",
                key=f"move_{log['id']}",
                value=log["id"] in st.session_state.logs_to_move,
            )
            if checked and log["id"] not in st.session_state.logs_to_move:
                st.session_state.logs_to_move.append(log["id"])
            elif not checked and log["id"] in st.session_state.logs_to_move:
                st.session_state.logs_to_move.remove(log["id"])
            display_col = cols[1]
            action_col = cols[2]
        else:
            display_col = cols[0]
            action_col = cols[1]

        with display_col:
            if log.get("type") == "image":
                st.image(log["text"], use_container_width=True)
            else:
                st.markdown(f"- {log['text']}")

        if not st.session_state.move_mode:
            with action_col:
                if not log.get("is_promoted") and log.get("type") == "text":
                    if st.button(
                        "↗️",
                        key=f"promote_{log['id']}",
                        help="Create a new topic from this log",
                    ):
                        new_topic = controller.promote_log_to_topic(
                            log, current_topic["id"]
                        )
                        st.session_state.current_topic_id = new_topic["id"]
                        st.rerun()
                elif log.get("is_promoted"):
                    st.markdown("*(Promoted)*")

    # --- Move Logs Footer ---
    if st.session_state.move_mode and st.session_state.logs_to_move:
        st.markdown("---")
        st.write(f"{len(st.session_state.logs_to_move)} logs selected.")

        # Exclude current topic from destination choices
        other_topics = [t for t in topics if t["id"] != current_topic["id"]]
        topic_options = {t["title"]: t["id"] for t in other_topics}

        if not other_topics:
            st.warning("No other topics available to move logs to.")
        else:
            selected_topic_title = st.selectbox(
                "Select destination topic:", options=list(topic_options.keys())
            )

            if st.button("Move Selected Logs"):
                target_topic_id = topic_options[selected_topic_title]
                controller.move_logs_to_topic(
                    st.session_state.logs_to_move, target_topic_id
                )
                st.success(
                    f"Successfully moved {len(st.session_state.logs_to_move)} logs to '{selected_topic_title}'."
                )
                # Reset and exit move mode
                st.session_state.move_mode = False
                st.session_state.logs_to_move = []
                st.rerun()


if __name__ == "__main__":
    main()
