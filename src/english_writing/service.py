from openai import OpenAI
from openai.types.chat import ChatCompletion

from .repository import QuestionRepository


class QuestionService:
    """
    Service to load and manage question data.
    """

    def __init__(self):
        self.repository = QuestionRepository()

    def load_questions(self) -> list[dict]:
        """
        Loads a list of questions from the database.
        """
        try:
            questions = self.repository.get_all()
            return [{"id": q.id, "question": q.question} for q in questions]
        except Exception as e:
            print(f"Error loading questions: {e}")
            return []


class FeedbackService:
    """
    Service to generate feedback for English answers by communicating with the OpenAI API.
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required.")
        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {e}")

    def get_feedback(self, question: str, answer: str) -> str:
        """
        Requests feedback from OpenAI based on the given question and answer.
        """
        system_prompt = """
        You are an expert English teacher.
        A student was given the following question:
        "{question}"

        The student provided this answer:
        "{answer}"

        Provide a sample revision (a simple, improved version) for reference.
        Also provide the feedback in Korean, starting with a brief overall summary and then detailing the points above in bullet form.
        
        Please provide constructive feedback on the student's answer.
        Focus on:
        1.  **Grammar:** Correct any grammatical errors per sentence.
        2.  **Vocabulary:** Suggest more appropriate or advanced vocabulary.
        3.  **Clarity & Flow:** Comment on the clarity and naturalness of the writing.
        4.  **Relevance:** Assess if the answer directly addresses the question.
        """

        formatted_prompt = system_prompt.format(question=question, answer=answer)

        try:
            response: ChatCompletion = self.client.chat.completions.create(
                model="gpt-5-nano",  # or "gpt-4"
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant acting as an English teacher.",
                    },
                    {"role": "user", "content": formatted_prompt},
                ],
            )

            feedback = response.choices[0].message.content
            if feedback:
                return feedback.strip()
            else:
                return "No valid feedback was received from OpenAI."

        except Exception as e:
            print(f"An error occurred during the OpenAI API call: {e}")
            return f"An error occurred while generating feedback: {e}"
