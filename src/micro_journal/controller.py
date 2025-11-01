from .service import MicroJournalService


class MicroJournalController:
    """
    Streamlit UI와 MicroJournalService를 연결하는 컨트롤러
    """

    def __init__(self, service: MicroJournalService):
        self._service = service

    def add_new_entry(self, content: str):
        """새로운 저널 항목을 추가합니다."""
        if not content or not content.strip():
            return  # 빈 내용은 추가하지 않음
        self._service.add_entry(content)

    def get_entries_for_display(self) -> list:
        """UI에 표시할 모든 저널 항목을 가져옵니다."""
        return self._service.get_all_entries()

    def get_weekly_summary(self) -> str:
        """주간 요약을 가져옵니다."""
        return self._service.get_summary(period="weekly")

    def get_monthly_summary(self) -> str:
        """월간 요약을 가져옵니다."""
        return self._service.get_summary(period="monthly")
