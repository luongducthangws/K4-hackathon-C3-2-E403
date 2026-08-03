"""Frontend dùng mã ngắn (day01/day02); DB dùng lecture_id đầy đủ do pipeline seed sinh ra."""

LECTURE_ALIAS = {
    "day01": "d1-ai-llm-foundation",
    "day02": "d2-xac-dinh-bai-toan",
}


def resolve_lecture_id(lecture_id: str) -> str:
    return LECTURE_ALIAS.get(lecture_id, lecture_id)
