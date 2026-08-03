from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Boolean, TIMESTAMP, func
from pgvector.sqlalchemy import Vector
from .database import Base


class Lecture(Base):
    __tablename__ = "lectures"

    lecture_id = Column(String, primary_key=True)
    title = Column(String)
    n_slides = Column(Integer)
    summary = Column(Text)


class Slide(Base):
    __tablename__ = "slides"

    lecture_id = Column(String, ForeignKey("lectures.lecture_id"), primary_key=True)
    slide_no = Column(Integer, primary_key=True)
    title = Column(String)
    body_text = Column(Text)
    image_url = Column(String)


class Concept(Base):
    __tablename__ = "concepts"

    concept_id = Column(String, primary_key=True)
    lecture_id = Column(String, ForeignKey("lectures.lecture_id"))
    name = Column(String)
    prereq_id = Column(String, ForeignKey("concepts.concept_id"), nullable=True)
    # embedding = Column(Vector(1536), nullable=True)  # P1, chưa dùng cho routing chatbot


class SlideConcept(Base):
    __tablename__ = "slide_concept"

    lecture_id = Column(String, primary_key=True)
    concept_id = Column(String, ForeignKey("concepts.concept_id"), primary_key=True)
    slide_start = Column(Integer, primary_key=True)
    slide_end = Column(Integer)


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True)
    concept_id = Column(String, ForeignKey("concepts.concept_id"))
    stem = Column(Text)
    options = Column(JSON)
    answer_idx = Column(Integer)
    explanation = Column(Text)
    item_elo = Column(Integer, default=1500)
    source_slide = Column(Integer)
    reviewed = Column(Boolean, default=False)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Mastery(Base):
    __tablename__ = "mastery"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    concept_id = Column(String, ForeignKey("concepts.concept_id"), primary_key=True)
    elo = Column(Integer, default=1400)
    n_attempts = Column(Integer, default=0)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Attempt(Base):
    __tablename__ = "attempts"

    attempt_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    question_id = Column(Integer, ForeignKey("questions.question_id"))
    correct = Column(Boolean)
    round_no = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
