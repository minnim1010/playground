from why_board.repository import task_repo, ai_response_repo
import streamlit as st
import openai


class TaskService:
    def add_task(self, title, description, why, how, caution):
        task = task_repo.add(
            title=title, description=description, why=why, how=how, caution=caution
        )
        return task

    def get_all_tasks(self):
        return task_repo.get_all_tasks()


class AIResponseService:
    def suggest_question_by_ai(self, task):
        """
        Generates and saves an AI suggestion for a given task.
        """
        suggestion = self._get_ai_suggestion(
            task["title"],
            task["description"],
            task["why"],
            task["how"],
            task["caution"],
        )
        if suggestion:
            ai_response_repo.add(task_id=task["id"], response=suggestion)
            return suggestion
        return None

    def get_responses_for_task(self, task_id):
        return ai_response_repo.get_for_task(task_id)

    def _get_ai_suggestion(self, task_title, task_description, why, how, caution):
        """
        Generates AI suggestions for a given task.
        """
        if not st.session_state.get("openai_api_key"):
            st.error("Please enter your OpenAI API key to get suggestions.")
            return None
        try:
            client = openai.OpenAI(api_key=st.session_state.openai_api_key)
            prompt = (
                f"You are an expert project reviewer helping someone think deeply about their work.\n"
                f"The task is titled: '{task_title}'\n"
                f"Description: {task_description}\n\n"
                f"Current thoughts:\n"
                f"- Purpose (why): {why}\n"
                f"- Implementation plan (how): {how}\n"
                f"- Risks or cautions: {caution}\n\n"
                f"Based on this information, generate 3–5 highly specific and practical self-reflection questions "
                f"that directly relate to the details of this task. Avoid generic or philosophical questions. "
                f"Each question should help refine the clarity, completeness, or feasibility of the plan.\n\n"
                f"Format the output as a short numbered list of concise questions."
            )
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                n=1,
                stop=None,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"An error occurred with the OpenAI API: {e}")
            return None


task_service = TaskService()
ai_response_service = AIResponseService()
