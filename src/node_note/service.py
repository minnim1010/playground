import json
import os
from datetime import datetime
import uuid

# --- Constants ---
DATA_FILE = "storage/private/node_note_data.json"

# --- Data File Management ---


def get_file_path():
    """Constructs the absolute path to the data file in the project root."""
    # Assumes the script is in a subdirectory of the project root.
    # This structure is /src/node_note/service.py, so we go up three levels.
    script_path = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_path, "..", ".."))
    return os.path.join(project_root, DATA_FILE)


def initialize_data():
    """Creates the data file with a root topic if it doesn't exist."""
    file_path = get_file_path()
    if not os.path.exists(file_path):
        root_topic_id = str(uuid.uuid4())
        initial_data = {
            "topics": [
                {
                    "id": root_topic_id,
                    "title": "Root",
                    "parent_topic_id": None,
                    "created_at": datetime.now().isoformat(),
                }
            ],
            "logs": [],
        }
        with open(file_path, "w") as f:
            json.dump(initial_data, f, indent=4)


def load_data():
    """Loads topics and logs from the JSON file."""
    initialize_data()  # Ensure file exists before reading
    file_path = get_file_path()
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is corrupted or not found, re-initialize and load again.
        initialize_data()
        return load_data()


def save_data(data):
    """Saves the entire data object back to the JSON file."""
    file_path = get_file_path()
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
