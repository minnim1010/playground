import os
import json
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from openai import OpenAI

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class AISchedulerService:
    def __init__(
        self, db_path: str = "storage/private/schedule.json", api_key: str | None = None
    ):
        self.db_path = db_path
        self._initialize_db()
        self.creds = self._get_google_credentials()
        self.client = OpenAI(api_key=api_key) if api_key else None

    # --- Task (JSON) Management ---
    def _initialize_db(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read_db(self) -> list:
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return []

    def _write_db(self, data: list):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_tasks(self) -> list:
        tasks = self._read_db()
        # Convert date strings from JSON to date objects
        for task in tasks:
            if isinstance(task.get("deadline"), str):
                task["deadline"] = datetime.datetime.strptime(
                    task["deadline"], "%Y-%m-%d"
                ).date()
        return sorted(tasks, key=lambda x: x.get("deadline", datetime.date.max))

    def add_task(self, task_data: dict):
        tasks = self._read_db()
        tasks.append(task_data)
        self._write_db(tasks)

    def update_task(self, task_id: str, updated_data: dict):
        tasks = self._read_db()
        for i, task in enumerate(tasks):
            if task.get("id") == task_id:
                tasks[i] = updated_data
                break
        self._write_db(tasks)

    def delete_task(self, task_id: str):
        tasks = self._read_db()
        tasks_to_keep = [task for task in tasks if task.get("id") != task_id]
        self._write_db(tasks_to_keep)

    # --- Google Calendar & AI ---
    def _get_google_credentials(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("credentials.json"):
                    raise FileNotFoundError("'credentials.json' file is required.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def find_available_slots(
        self,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        duration_minutes: int,
    ) -> list:
        try:
            service = build("calendar", "v3", credentials=self.creds)
            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=start_time.isoformat(),
                    timeMax=end_time.isoformat(),
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            free_slots = []
            previous_event_end = start_time
            for event in events:
                event_start = datetime.datetime.fromisoformat(
                    event["start"].get("dateTime")
                )
                if (
                    event_start - previous_event_end
                ).total_seconds() >= duration_minutes * 60:
                    free_slots.append((previous_event_end, event_start))
                previous_event_end = datetime.datetime.fromisoformat(
                    event["end"].get("dateTime")
                )
            if (end_time - previous_event_end).total_seconds() >= duration_minutes * 60:
                free_slots.append((previous_event_end, end_time))
            return free_slots
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_ai_recommendations(self, task_info: dict, slots: list):
        if not self.client:
            return "OpenAI API key is not set, so AI recommendations are not available."
        if not slots:
            return None

        # Construct the prompt for the AI
        prompt_slots = "\n".join(
            [
                f"{i}: {slot[0].strftime('%Y-%m-%d %H:%M')} - {slot[1].strftime('%H:%M')}"
                for i, slot in enumerate(slots)
            ]
        )
        prompt = f"""
        You are an expert scheduler. Based on the task details and the available time slots, recommend the best slot.
        Today is {datetime.datetime.now().strftime('%Y-%m-%d %A')}.

        Task Details:
        - Name: {task_info.get('name')}
        - Deadline: {task_info.get('deadline')}
        - Duration: {task_info.get('duration')} hours
        - Urgent: {"Yes" if task_info.get('urgent') else "No"}

        Available Slots:
        {prompt_slots}

        Consider the deadline, urgency, and the time of day (e.g., prefer work hours for focused tasks). 
        Respond with only the index number of the best slot.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful scheduling assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
            )

            # Extract the index from the AI's response
            best_slot_index = int(response.choices[0].message.content.strip())

            if 0 <= best_slot_index < len(slots):
                return slots[best_slot_index]
            else:
                # Fallback if the index is out of range
                return slots[0]
        except (ValueError, IndexError, Exception) as e:
            print(
                f"AI recommendation failed: {e}. Falling back to the first available slot."
            )
            # Fallback to the first slot in case of any error
            return slots[0]

    def create_calendar_event(
        self,
        summary: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        description: str,
    ):
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Seoul"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Seoul"},
        }
        try:
            service = build("calendar", "v3", credentials=self.creds)
            created_event = (
                service.events().insert(calendarId="primary", body=event).execute()
            )
            return created_event.get("htmlLink")
        except Exception as e:
            print(f"An error occurred while creating event: {e}")
            return None
