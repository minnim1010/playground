import streamlit as st
from k8s_command_runner.controller import (
    initialize_session_state,
    update_callbacks,
    get_pods_logic,
    handle_pod_specific_commands,
    run_specific_command,
    parse_pod_info,
    CONTEXT_MAP,
    ENVS,
)


def main_page():
    st.set_page_config(layout="wide")
    st.title("K8s Command Runner")

    initialize_session_state()

    # --- User Input Section ---
    st.header("Get Pods")

    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 2, 2])
    with col1:
        env = st.selectbox(
            "Environment", ENVS, key="selected_env", on_change=update_callbacks
        )
    with col2:
        region_options = list(CONTEXT_MAP[env].keys())
        region = st.selectbox(
            "Region", region_options, key="selected_region", on_change=update_callbacks
        )
    with col3:
        context_options = CONTEXT_MAP[env][region]
        kubecontext = st.selectbox(
            "Kubernetes Context", context_options, key="kubecontext"
        )
    with col4:
        namespace = st.text_input("Namespace", "debezium", key="namespace")
    with col5:
        grep_filter = st.text_input("Filter pods using | grep", key="grep_filter")

    # --- Command Execution ---
    cmd_col, btn_col = st.columns([5, 1])
    with btn_col:
        st.write("")
        if st.button("Get Pods", use_container_width=True):
            full_command_str = get_pods_logic(kubecontext, namespace, grep_filter)
            with cmd_col:
                st.info(f"**Generated Command:** `{full_command_str}`")

    # --- Display Output ---
    if st.session_state.error_info:
        st.error(st.session_state.error_info)
    elif st.session_state.pod_info:
        parse_pod_info(st.session_state.pod_info, grep_filter)

    st.divider()

    # Bottom half: Command Execution
    st.header("Pod Specific Commands")

    pod_name_col, logs_col, desc_col = st.columns([4, 1, 1])

    with pod_name_col:
        st.text_input("Pod Name", key="pod_name", label_visibility="collapsed")

    with logs_col:
        if st.button("Logs -f", use_container_width=True, key="logs_button"):
            handle_pod_specific_commands(kubecontext, namespace)

    with desc_col:
        if st.button("Describe Pod", use_container_width=True, key="describe_button"):
            handle_pod_specific_commands(kubecontext, namespace)

    command_input_col, run_button_col = st.columns([5, 1])
    with command_input_col:
        st.text_input(
            "Command to execute:", key="command", label_visibility="collapsed"
        )
    with run_button_col:
        run_command_clicked = st.button("Run Command", use_container_width=True)

    # --- Pod Specific Command Output ---
    # This section is now outside the column layout to ensure full width.
    if run_command_clicked:
        stream_output = run_specific_command()
        if stream_output:
            log_output_area = st.empty()
            full_log_output = ""
            try:
                for line in stream_output:
                    full_log_output += line
                    log_output_area.code(full_log_output, language="bash")
            except Exception as e:
                st.session_state.error = f"An error occurred during streaming: {e}"

    # Display output from 'Logs' or 'Describe' commands
    if st.session_state.output:
        st.code(st.session_state.output, language="bash")

    # Display any errors
    if st.session_state.error:
        st.subheader("Errors:")
        st.code(st.session_state.error, language="bash")


if __name__ == "__main__":
    main_page()
