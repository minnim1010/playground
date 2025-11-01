from .service import AISchedulerService
import datetime
import uuid


class AISchedulerController:
    def __init__(self, service: AISchedulerService):
        self._service = service

    # --- Task Management ---
    def get_all_tasks(self) -> list:
        """Gets all tasks to be displayed in the UI."""
        return self._service.get_tasks()

    def add_task(
        self,
        name: str,
        deadline: datetime.date,
        duration: int,
        urgent: bool,
        description: str,
    ):
        """Adds a new task."""
        task_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            # Convert date to string for JSON storage
            "deadline": deadline.isoformat(),
            "duration": duration,
            "urgent": urgent,
            "completed": False,
        }
        self._service.add_task(task_data)

    def update_task(
        self,
        task_id: str,
        name: str,
        deadline: datetime.date,
        duration: int,
        urgent: bool,
        completed: bool,
        description: str,
    ):
        """Updates an existing task."""
        task_data = {
            "id": task_id,
            "name": name,
            "description": description,
            "deadline": deadline.isoformat(),
            "duration": duration,
            "urgent": urgent,
            "completed": completed,
        }
        self._service.update_task(task_id, task_data)

    def delete_task(self, task_id: str):
        """Deletes a task."""
        self._service.delete_task(task_id)

    def get_task_by_id(self, task_id: str):
        """Gets specific task information by ID."""
        tasks = self.get_all_tasks()
        return next((task for task in tasks if task["id"] == task_id), None)

    # --- AI Scheduling ---
    def find_and_recommend_time(self, task_id: str):
        """Gets AI recommendations for the selected task."""
        task = self.get_task_by_id(task_id)
        if not task:
            return {"error": "Selected task not found."}

        if not self._service.creds:
            return {"error": "Google Calendar authentication is required."}

        now = datetime.datetime.now(datetime.timezone.utc)
        deadline_date = task["deadline"]
        end_of_deadline = datetime.datetime.combine(
            deadline_date, datetime.time(23, 59, 59), tzinfo=datetime.timezone.utc
        )
        duration_minutes = task["duration"] * 60

        available_slots = self._service.find_available_slots(
            now, end_of_deadline, duration_minutes
        )

        if not available_slots:
            return {
                "recommendations": [],
                "message": "Could not find enough free time in the selected period.",
            }

        task_info = {k: v for k, v in task.items() if k != "id"}
        recommended_slot = self._service.get_ai_recommendations(
            task_info, available_slots
        )

        recommendations = [
            {
                "start": slot[0],
                "end": slot[0] + datetime.timedelta(minutes=duration_minutes),
            }
            for slot in [recommended_slot]
            if recommended_slot
        ]

        return {
            "recommendations": recommendations,
            "message": f"{len(recommendations)} time slots recommended.",
        }

    def schedule_event(
        self,
        task_name: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        description: str,
    ):
        """Registers an event in the calendar."""
        return self._service.create_calendar_event(
            task_name, start_time, end_time, description
        )
