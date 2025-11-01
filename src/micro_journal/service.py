import json
import os
from datetime import datetime, timedelta
from openai import OpenAI


class MicroJournalService:
    """
    마이크로 저널 데이터 관리 및 AI 요약을 담당하는 서비스
    """

    def __init__(self, db_path: str = "micro_journal.json", api_key: str | None = None):
        self.db_path = db_path
        self.client = OpenAI(api_key=api_key) if api_key else None
        self._initialize_db()

    def _initialize_db(self):
        """데이터베이스 파일이 없으면 초기화합니다."""
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def add_entry(self, content: str):
        """새로운 저널 항목을 추가합니다."""
        try:
            with open(self.db_path, "r+", encoding="utf-8") as f:
                entries = json.load(f)
                new_entry = {
                    "id": len(entries) + 1,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                }
                entries.append(new_entry)
                f.seek(0)
                json.dump(entries, f, ensure_ascii=False, indent=4)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error adding entry: {e}")  # 실제 앱에서는 로깅으로 대체해야 합니다.

    def get_all_entries(self) -> list:
        """모든 저널 항목을 최신순으로 가져옵니다."""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                entries = json.load(f)
                return sorted(entries, key=lambda x: x["timestamp"], reverse=True)
        except (IOError, json.JSONDecodeError):
            return []

    def get_summary(self, period: str = "weekly") -> str:
        """
        지정된 기간(주간/월간)의 저널 항목을 AI를 사용하여 요약합니다.
        """
        if not self.client:
            return (
                "OpenAI API 키가 설정되지 않았습니다. 요약 기능을 사용할 수 없습니다."
            )

        all_entries = self.get_all_entries()
        if not all_entries:
            return "요약할 기록이 아직 없습니다."

        # 기간에 맞는 항목 필터링
        now = datetime.now()
        if period == "weekly":
            start_date = (now - timedelta(days=now.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            period_name = "주"
        elif period == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_name = "월"
        else:
            return "지원되지 않는 기간입니다."

        relevant_entries = [
            entry
            for entry in all_entries
            if datetime.fromisoformat(entry["timestamp"]) >= start_date
        ]

        if not relevant_entries:
            return f"이번 {period_name}에는 기록이 없습니다."

        # 프롬프트 생성
        entries_str = "\n".join([f"- {entry['content']}" for entry in relevant_entries])

        base_prompt = """너는 나의 기록을 바탕으로 회고를 도와주는 코치야. 다음의 일기들을 읽고 아래 항목을 생성해줘.

{entries}

1. 이번 {period}의 핵심 키워드 3개
2. 주요 사건 요약 (2~3문장)
3. 나의 감정 패턴 (긍정/부정/중립 비율 포함)
4. 배운 점 혹은 깨달음 2가지
5. 다음 {next_period}를 위한 한 줄 조언

출력은 아래 형식으로 해줘:
---
**핵심 키워드:** ...
**요약:** ...
**감정 요약:** ...
**배운 점:** ...
**다음 주 조언:** ...
---
"""

        if period == "weekly":
            prompt = base_prompt.format(
                entries=entries_str, period="주", next_period="주"
            )
        else:  # monthly
            prompt = base_prompt.format(
                entries=entries_str, period="달", next_period="달"
            )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful coaching assistant who provides insightful reflections based on journal entries.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            summary = response.choices[0].message.content
            return summary if summary else "AI로부터 요약을 생성하지 못했습니다."
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")  # 실제 앱에서는 로깅으로 대체
            return "AI 요약 생성 중 오류가 발생했습니다. API 키와 네트워크 연결을 확인해주세요."
