"""Elo engine thuần toán, không gọi LLM. Công thức theo mục 4 của master doc."""

D_REF = 1500  # độ khó chuẩn cố định để tính mastery
K_PRIME = 8   # item_elo chỉ nên nhích chậm


def expected(rating_a: float, rating_b: float) -> float:
    """Xác suất A thắng B (ở đây: xác suất trả lời đúng)."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def k_factor(n_attempts: int) -> int:
    return 40 if n_attempts < 10 else 20


def update_elo(user_elo: int, item_elo: int, n_attempts: int, correct: bool) -> tuple[int, int]:
    """Trả về (user_elo_moi, item_elo_moi)."""
    y = 1 if correct else 0
    p = expected(user_elo, item_elo)
    k = k_factor(n_attempts)
    new_user_elo = round(user_elo + k * (y - p))
    new_item_elo = round(item_elo - K_PRIME * (y - p))
    return new_user_elo, new_item_elo


def mastery_pct(user_elo: int) -> float:
    return expected(user_elo, D_REF) * 100


def mastery_state(user_elo: int, n_attempts: int) -> str:
    pct = mastery_pct(user_elo)
    if pct >= 75 and n_attempts >= 5:
        return "mastered"
    if pct >= 50:
        return "learning"
    return "weak"


def survey_prior(v: int) -> int:
    """Khởi tạo Elo từ khảo sát đầu vào, v trong [1,5]."""
    return 1200 + 100 * v
