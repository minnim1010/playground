import subprocess

import streamlit as st
from k8s_command_runner.service import run_kubectl_command, stream_command
import pandas as pd
from io import StringIO

# --- Data and State Initialization ---
CONTEXT_MAP = {
    "staging": {
        "eu": ["k8s-staging-eu-shared-1"],
    },
    "load-tests": {
        "eu": ["k8s-load-tests-eu-shared-1"],
    },
    "production": {
        "eu": [
            "k8s-production-eu-cluster-0",
            "k8s-production-eu-cluster-1",
            "k8s-production-eu-cluster-2",
            "k8s-production-eu-cluster-3",
            "k8s-production-eu-cluster-4",
            "k8s-production-eu-cluster-5",
            "k8s-production-eu-cluster-6",
            "eu01-infra02",
        ],
        "us": [
            "k8s-production-us-cluster-0",
            "k8s-production-us-cluster-1",
        ],
        "ap": [
            "k8s-production-ap-cluster-0",
            "k8s-production-ap-cluster-2",
            "k8s-production-ap-cluster-3",
            "k8s-production-ap-cluster-4",
            "k8s-production-ap-cluster-5",
            "k8s-production-ap-cluster-6",
        ],
        "kr2": [
            "k8s-production-kr2-cluster-0",
        ],
    },
}
ENVS = list(CONTEXT_MAP.keys())


def initialize_session_state():
    """Initializes session state for the application."""
    if "selected_env" not in st.session_state:
        st.session_state.selected_env = ENVS[0]
    if "selected_region" not in st.session_state:
        st.session_state.selected_region = list(
            CONTEXT_MAP[st.session_state.selected_env].keys()
        )[0]
    if "pod_info" not in st.session_state:
        st.session_state.pod_info = None
    if "error_info" not in st.session_state:
        st.session_state.error_info = None
    if "command" not in st.session_state:
        st.session_state.command = ""
    if "output" not in st.session_state:
        st.session_state.output = ""
    if "error" not in st.session_state:
        st.session_state.error = ""
    if "pod_name" not in st.session_state:
        st.session_state.pod_name = ""


def update_callbacks():
    """Callback to reset region if it's not valid for the selected env."""
    if (
        st.session_state.selected_region
        not in CONTEXT_MAP[st.session_state.selected_env]
    ):
        st.session_state.selected_region = list(
            CONTEXT_MAP[st.session_state.selected_env].keys()
        )[0]


def get_pods_logic(kubecontext, namespace, grep_filter):
    """Handles the logic for the 'Get Pods' button click."""
    st.cache_data.clear()
    command_list = ["kubectl", "get", "pods", "--context", kubecontext, "-n", namespace]
    full_command_str = " ".join(command_list)
    if grep_filter:
        full_command_str += f" | grep '{grep_filter}'"

    command_to_run = full_command_str if grep_filter else command_list
    use_shell_for_run = bool(grep_filter)
    st.session_state.pod_info, st.session_state.error_info = run_kubectl_command(
        command_to_run, use_shell_for_run
    )
    return full_command_str


def handle_pod_specific_commands(kubecontext, namespace):
    """Handles the logic for pod-specific commands like 'Logs -f' and 'Describe Pod'."""
    if st.session_state.pod_name:
        if st.session_state.get("logs_button"):
            st.session_state.command = f"kubectl logs -f {st.session_state.pod_name} --context {kubecontext} -n {namespace}"
        elif st.session_state.get("describe_button"):
            st.session_state.command = f"kubectl describe pod {st.session_state.pod_name} --context {kubecontext} -n {namespace}"
    else:
        st.warning("Please enter a Pod Name.")
        st.session_state.command = ""


def run_specific_command():
    """Handles the logic for the 'Run Command' button."""
    st.session_state.output = ""
    st.session_state.error = ""
    if st.session_state.command:
        if "logs -f" in st.session_state.command:
            return stream_command(st.session_state.command)
        else:
            try:
                result = subprocess.run(
                    st.session_state.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                st.session_state.output = result.stdout
                st.session_state.error = result.stderr
            except subprocess.TimeoutExpired:
                st.session_state.error = "Error: Command timed out."
            except Exception as e:
                st.session_state.error = f"An error occurred: {e}"
    else:
        st.session_state.error = "Please enter or generate a command."
    return None


def parse_pod_info(pod_info, grep_filter):
    """Parses and displays the pod information."""
    if "No matching pods found" in pod_info:
        st.info(pod_info)
    elif grep_filter:
        st.code(pod_info, language="bash")
    else:
        try:
            string_io = StringIO(pod_info)
            df = pd.read_fwf(string_io)
            if df.empty:
                st.info("No pods found in the selected context.")
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not parse kubectl output into a table: {e}")
            st.text("Displaying raw text instead.")
            st.code(pod_info)
