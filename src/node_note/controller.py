from . import service
from datetime import datetime
import uuid
import os

IMG_DIR = "img"

# --- Topic Management ---


def get_all_topics():
    """Retrieves all topics from the data source."""
    data = service.load_data()
    return data.get("topics", [])


def create_topic(title, parent_topic_id):
    """Creates a new topic and returns it."""
    if not title or not parent_topic_id:
        return None
    data = service.load_data()
    new_topic = {
        "id": str(uuid.uuid4()),
        "title": title,
        "parent_topic_id": parent_topic_id,
        "created_at": datetime.now().isoformat(),
    }
    data["topics"].append(new_topic)
    service.save_data(data)
    return new_topic


# --- Log Management ---


def get_logs_for_topic(topic_id):
    """Retrieves all logs associated with a specific topic."""
    data = service.load_data()
    return [log for log in data.get("logs", []) if log["topic_id"] == topic_id]


def get_all_logs():
    """Retrieves all logs from the data source."""
    data = service.load_data()
    return data.get("logs", [])


def add_log(text, topic_id):
    """Adds a new text log to a topic."""
    if not text or not topic_id:
        return
    data = service.load_data()
    new_log = {
        "id": str(uuid.uuid4()),
        "text": text,
        "topic_id": topic_id,
        "type": "text",
        "is_promoted": False,
        "created_at": datetime.now().isoformat(),
    }
    data["logs"].append(new_log)
    service.save_data(data)


def add_image_log(uploaded_file, topic_id):
    """Saves an uploaded image and adds a new image log to a topic."""
    if not uploaded_file or not topic_id:
        return None

    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)

    filename = os.path.basename(uploaded_file.name)
    filepath = os.path.join(IMG_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    data = service.load_data()
    new_log = {
        "id": str(uuid.uuid4()),
        "text": filepath,
        "topic_id": topic_id,
        "type": "image",
        "created_at": datetime.now().isoformat(),
    }
    data["logs"].append(new_log)
    service.save_data(data)
    return new_log


def move_logs_to_topic(log_ids, target_topic_id):
    """Moves a list of logs to a new parent topic."""
    if not log_ids or not target_topic_id:
        return

    data = service.load_data()
    logs_updated = False
    for log in data.get("logs", []):
        if log["id"] in log_ids:
            log["topic_id"] = target_topic_id
            logs_updated = True

    if logs_updated:
        service.save_data(data)


# --- Log Promotion ---


def promote_log_to_topic(log, current_topic_id):
    """Promotes a text log to a new topic and marks the log as promoted."""
    if log.get("type", "text") != "text":
        return None

    data = service.load_data()

    # 1. Create a new topic from the log
    new_topic = {
        "id": str(uuid.uuid4()),
        "title": log["text"],
        "parent_topic_id": current_topic_id,
        "created_at": datetime.now().isoformat(),
    }
    data["topics"].append(new_topic)

    # 2. Mark the original log as promoted
    for lo in data["logs"]:
        if lo["id"] == log["id"]:
            lo["is_promoted"] = True
            break

    service.save_data(data)
    return new_topic
