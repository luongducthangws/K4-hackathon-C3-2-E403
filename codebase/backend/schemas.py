from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    lecture_id: str
    slide_no: int
    question: str


class ChatResponse(BaseModel):
    answer: str


class RegisterRequest(BaseModel):
    name: str
    email: str


class LoginRequest(BaseModel):
    email: str


class UserOut(BaseModel):
    user_id: int
    name: str
    email: str


class SurveyRating(BaseModel):
    concept_id: str
    v: int  # 1-5, tự đánh giá


class SurveyRequest(BaseModel):
    lecture_id: str
    ratings: List[SurveyRating]


class MasteryOut(BaseModel):
    concept_id: str
    name: str
    elo: int
    mastery: float
    state: str
    n_attempts: int


class AttemptRequest(BaseModel):
    question_id: int
    answer_idx: int
    round_no: int = 1


class AttemptResponse(BaseModel):
    correct: bool
    correct_answer_idx: int
    explanation: Optional[str] = None
    elo_delta: int
    user_elo_new: int
    mastery_new: float
    item_elo_new: int


class ReviewSlideRange(BaseModel):
    concept_id: str
    concept_name: str
    mastery: float
    slide_start: int
    slide_end: int


class QuizGenerateRequest(BaseModel):
    lecture_id: str
    concept_ids: List[str] = []
    difficulty: str = "auto"  # auto | easy | challenge
    num_questions: int = 5
