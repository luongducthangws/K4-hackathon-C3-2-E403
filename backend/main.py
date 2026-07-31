import json
import os
from datetime import datetime, timezone
from typing import List, Optional

import google.generativeai as genai
import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.orm import Session

from . import elo as elo_mod
from .database import get_db
from .graph import app as graph_app
from .lecture_alias import resolve_lecture_id
from .models import Attempt, Concept, Mastery, Question, Slide, SlideConcept, User
from .schemas import (
    AttemptRequest,
    AttemptResponse,
    ChatRequest,
    LoginRequest,
    MasteryOut,
    QuizGenerateRequest,
    RegisterRequest,
    ReviewSlideRange,
    SurveyRequest,
    UserOut,
)

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FPT_API_KEY = os.environ.get("FPT_API_KEY")
FPT_API_URL = os.environ.get("FPT_API_URL", "https://mkp-api.fptcloud.com/chat/completions")
FPT_MODEL = os.environ.get("FPT_MODEL", "GLM-5.2")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vlearn-adaptive-loop-v7.html")
    return FileResponse(html_path)


@app.post("/chat")
def chat_with_slide(
    request: ChatRequest,
    user_id: str = Header(None),
    db: Session = Depends(get_db),
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user_id in headers")
    if not GEMINI_API_KEY and not FPT_API_KEY:
        raise HTTPException(status_code=503, detail="Chưa cấu hình API Key (GEMINI_API_KEY hoặc FPT_API_KEY) trên server")

    thread_id = f"{user_id}_{request.lecture_id}"
    config = {"configurable": {"thread_id": thread_id}}

    try:
        state = graph_app.invoke(
            {"messages": [HumanMessage(content=request.question)], "lecture_id": request.lecture_id},
            config=config,
        )

        if not state.get("is_relevant", True):
            final_message = state["messages"][-1].content

            def generate_rejection():
                yield f"data: {json.dumps({'answer': final_message}, ensure_ascii=False)}\n\n"

            return StreamingResponse(generate_rejection(), media_type="text/event-stream")

        context = state.get("context", "")
        lecture_id = state.get("lecture_id", request.lecture_id)
        sys_prompt = f"""Bạn là VLearn Tutor, trợ lý AI giải đáp thắc mắc về bài giảng.
Bạn đang hỗ trợ học viên trong bài học {lecture_id}.

[TÓM TẮT & CÁC SLIDE LIÊN QUAN]:
{context}

Nhiệm vụ của bạn:
1. CHỈ TRẢ LỜI các câu hỏi tập trung vào kiến thức của bài học và lĩnh vực chuyên môn.
2. KHÔNG ĐƯỢC trả lời những vấn đề không liên quan đến đề tài. Nếu học viên hỏi ngoài lề, hãy lịch sự từ chối và hướng họ quay lại với nội dung bài học.
3. Dựa vào các nội dung trên và lịch sử hội thoại, hãy trả lời ngắn gọn, súc tích, dễ hiểu. KHÔNG bịa đặt thông tin nếu không có trong ngữ cảnh — nếu ngữ cảnh không đủ, nói rõ "chưa đủ dữ liệu" thay vì đoán.
4. Khi dùng nội dung từ một slide cụ thể, TRÍCH SỐ SLIDE nguồn ngay trong câu trả lời, ví dụ "(Slide 8)", để học viên kiểm chứng lại được.
5. Nếu câu hỏi không rõ ràng về bài giảng, hãy hỏi lại học viên để làm rõ ý và hướng họ về việc hỏi đáp kiến thức bài học."""

        def generate():
            full_answer = ""
            if FPT_API_KEY:
                formatted_msgs = [{"role": "system", "content": sys_prompt}]
                for msg in state["messages"]:
                    role = "assistant" if msg.type == "ai" else "user"
                    if msg.type != "system":
                        formatted_msgs.append({"role": role, "content": msg.content})

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {FPT_API_KEY}",
                }
                data = {
                    "model": FPT_MODEL,
                    "messages": formatted_msgs,
                    "stream": True,
                    "temperature": 0.1,
                }

                response = requests.post(FPT_API_URL, headers=headers, json=data, stream=True, timeout=120)
                if not response.ok:
                    error = f"Lỗi gọi API: {response.text}"
                    yield f"data: {json.dumps({'answer': error}, ensure_ascii=False)}\n\n"
                    return

                for line in response.iter_lines():
                    if not line:
                        continue
                    line_text = line.decode("utf-8")
                    if line_text.startswith("data: "):
                        line_text = line_text[6:]
                    if line_text == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(line_text)
                    except json.JSONDecodeError:
                        continue

                    choices = chunk_data.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})
                    content = delta.get("content", "")
                    reasoning = delta.get("reasoning_content", "")
                    if content:
                        full_answer += content
                    if content or reasoning:
                        yield f"data: {json.dumps({'answer': content, 'reasoning': reasoning}, ensure_ascii=False)}\n\n"
            else:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain_core.messages import SystemMessage

                gemini_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.1)
                langchain_msgs = [SystemMessage(content=sys_prompt)]
                for msg in state["messages"]:
                    if msg.type != "system":
                        langchain_msgs.append(msg)

                for chunk in gemini_llm.stream(langchain_msgs):
                    content = chunk.content
                    if content:
                        if isinstance(content, list):
                            text_content = "".join([item.get("text", "") for item in content if isinstance(item, dict) and "text" in item])
                        else:
                            text_content = str(content)
                        full_answer += text_content
                        yield f"data: {json.dumps({'answer': text_content, 'reasoning': ''}, ensure_ascii=False)}\n\n"

            graph_app.update_state(config, {"messages": [AIMessage(content=full_answer)]})

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        print(f"Error in graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Static slides ============
slides_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vlearn-pack", "slides")


@app.get("/debug_slides")
def debug_slides():
    return {
        "dir": slides_dir,
        "exists": os.path.exists(slides_dir),
        "files": os.listdir(slides_dir) if os.path.exists(slides_dir) else [],
    }


app.mount("/static_slides", StaticFiles(directory=slides_dir), name="static_slides")


@app.get("/slides/{lecture_id}/{slide_no}")
def get_slide(lecture_id: str, slide_no: int, db: Session = Depends(get_db)):
    real_lecture_id = resolve_lecture_id(lecture_id)
    slide = db.query(Slide).filter(
        Slide.lecture_id == real_lecture_id,
        Slide.slide_no == slide_no,
    ).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    return {"title": slide.title, "body_text": slide.body_text}


# ============ Helpers dùng chung cho Elo/mastery ============
def _get_user(db: Session, x_user_id: Optional[int]) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Thiếu header X-User-Id")
    user = db.query(User).filter(User.user_id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return user


def _mastery_or_default(db: Session, user_id: int, concept_id: str) -> tuple[int, int]:
    row = db.query(Mastery).filter(Mastery.user_id == user_id, Mastery.concept_id == concept_id).first()
    if row:
        return row.elo, row.n_attempts
    return 1400, 0


def _mastery_out_list(db: Session, user_id: int, lecture_id: str) -> List[MasteryOut]:
    concepts = db.query(Concept).filter(Concept.lecture_id == lecture_id).all()
    out = []
    for c in concepts:
        elo_val, n = _mastery_or_default(db, user_id, c.concept_id)
        out.append(MasteryOut(
            concept_id=c.concept_id,
            name=c.name,
            elo=elo_val,
            mastery=round(elo_mod.mastery_pct(elo_val), 1),
            state=elo_mod.mastery_state(elo_val, n),
            n_attempts=n,
        ))
    return out


# ============ Auth (tối giản cho demo — không có mật khẩu trong DB thật) ============
@app.post("/auth/register", response_model=UserOut, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        return UserOut(user_id=existing.user_id, name=existing.name, email=existing.email)
    user = User(name=req.name, email=req.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(user_id=user.user_id, name=user.name, email=user.email)


@app.post("/auth/login", response_model=UserOut)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email chưa đăng ký")
    return UserOut(user_id=user.user_id, name=user.name, email=user.email)


# ============ Mastery / survey / review-path / attempts ============
@app.post("/users/me/survey", response_model=List[MasteryOut])
def submit_survey(req: SurveyRequest, x_user_id: Optional[int] = Header(None), db: Session = Depends(get_db)):
    user = _get_user(db, x_user_id)
    real_lecture_id = resolve_lecture_id(req.lecture_id)
    for r in req.ratings:
        row = db.query(Mastery).filter(Mastery.user_id == user.user_id, Mastery.concept_id == r.concept_id).first()
        if row and row.n_attempts > 0:
            continue
        prior = elo_mod.survey_prior(r.v)
        if row:
            row.elo = prior
        else:
            db.add(Mastery(user_id=user.user_id, concept_id=r.concept_id, elo=prior, n_attempts=0))
    db.commit()
    return _mastery_out_list(db, user.user_id, real_lecture_id)


@app.get("/users/me/mastery", response_model=List[MasteryOut])
def get_mastery(lecture_id: str, x_user_id: Optional[int] = Header(None), db: Session = Depends(get_db)):
    user = _get_user(db, x_user_id)
    return _mastery_out_list(db, user.user_id, resolve_lecture_id(lecture_id))


@app.post("/attempts", response_model=AttemptResponse)
def submit_attempt(req: AttemptRequest, x_user_id: Optional[int] = Header(None), db: Session = Depends(get_db)):
    user = _get_user(db, x_user_id)
    question = db.query(Question).filter(Question.question_id == req.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Câu hỏi không tồn tại")

    correct = req.answer_idx == question.answer_idx

    mastery = db.query(Mastery).filter(
        Mastery.user_id == user.user_id, Mastery.concept_id == question.concept_id
    ).first()
    if not mastery:
        mastery = Mastery(user_id=user.user_id, concept_id=question.concept_id, elo=1400, n_attempts=0)
        db.add(mastery)
        db.flush()

    new_user_elo, new_item_elo = elo_mod.update_elo(
        mastery.elo, question.item_elo or 1500, mastery.n_attempts, correct
    )
    elo_delta = new_user_elo - mastery.elo

    mastery.elo = new_user_elo
    mastery.n_attempts += 1
    mastery.updated_at = datetime.now(timezone.utc)
    question.item_elo = new_item_elo

    db.add(Attempt(
        user_id=user.user_id,
        question_id=question.question_id,
        correct=correct,
        round_no=req.round_no,
    ))
    db.commit()

    return AttemptResponse(
        correct=correct,
        correct_answer_idx=question.answer_idx,
        explanation=question.explanation,
        elo_delta=elo_delta,
        user_elo_new=new_user_elo,
        mastery_new=round(elo_mod.mastery_pct(new_user_elo), 1),
        item_elo_new=new_item_elo,
    )


@app.get("/users/me/review-path", response_model=List[ReviewSlideRange])
def review_path(lecture_id: str, x_user_id: Optional[int] = Header(None), db: Session = Depends(get_db)):
    user = _get_user(db, x_user_id)
    real_lecture_id = resolve_lecture_id(lecture_id)
    concepts = db.query(Concept).filter(Concept.lecture_id == real_lecture_id).all()
    if not concepts:
        return []

    scored = [(c, _mastery_or_default(db, user.user_id, c.concept_id)[0]) for c in concepts]
    weak = [(c, e) for c, e in scored if elo_mod.mastery_pct(e) < 50]
    if not weak:
        weak = sorted(scored, key=lambda x: x[1])[:1]
    weak.sort(key=lambda x: x[1])

    weak_by_id = {c.concept_id: (c, e) for c, e in weak}
    ordered: List[tuple] = []
    seen: set = set()

    def emit(c, e):
        if c.concept_id in seen:
            return
        if c.prereq_id in weak_by_id and c.prereq_id not in seen:
            prereq_c, prereq_e = weak_by_id[c.prereq_id]
            emit(prereq_c, prereq_e)
        seen.add(c.concept_id)
        ordered.append((c, e))

    for c, e in weak:
        emit(c, e)

    result: List[ReviewSlideRange] = []
    for c, e in ordered[:5]:
        ranges = db.query(SlideConcept).filter(
            SlideConcept.lecture_id == real_lecture_id,
            SlideConcept.concept_id == c.concept_id,
        ).all()
        for r in ranges:
            start = max(1, r.slide_start - 1)
            end = (r.slide_end or r.slide_start) + 1
            result.append(ReviewSlideRange(
                concept_id=c.concept_id,
                concept_name=c.name,
                mastery=round(elo_mod.mastery_pct(e), 1),
                slide_start=start,
                slide_end=end,
            ))
        if len(result) >= 5:
            break
    return result[:5]


# ============ Concepts & quiz generation ============
@app.get("/concepts/{lecture_id}")
def get_concepts(lecture_id: str, x_user_id: Optional[int] = Header(None), db: Session = Depends(get_db)):
    real_lecture_id = resolve_lecture_id(lecture_id)
    concepts = db.query(Concept).filter(Concept.lecture_id == real_lecture_id).all()

    result = []
    for c in concepts:
        elo_val = 1400
        n_att = 0
        if x_user_id:
            elo_val, n_att = _mastery_or_default(db, x_user_id, c.concept_id)
        slide_range = db.query(SlideConcept).filter(
            SlideConcept.lecture_id == real_lecture_id,
            SlideConcept.concept_id == c.concept_id,
        ).first()
        slides = list(range(slide_range.slide_start, slide_range.slide_end + 1)) if slide_range else []
        result.append({"id": c.concept_id, "name": c.name, "elo": elo_val, "n_attempts": n_att, "slides": slides})
    return result


@app.post("/quiz/generate")
def generate_quiz(req: QuizGenerateRequest, x_user_id: Optional[int] = Header(None), db: Session = Depends(get_db)):
    real_lecture_id = resolve_lecture_id(req.lecture_id)

    concept_ids = req.concept_ids
    if not concept_ids:
        concepts = db.query(Concept).filter(Concept.lecture_id == real_lecture_id).all()
        if x_user_id:
            concepts.sort(key=lambda c: _mastery_or_default(db, x_user_id, c.concept_id)[0])
        concept_ids = [c.concept_id for c in concepts[:3]]

    done_ids = set()
    if x_user_id:
        done_ids = {row[0] for row in db.query(Attempt.question_id).filter(Attempt.user_id == x_user_id).all()}

    base_query = db.query(Question).filter(
        Question.concept_id.in_(concept_ids),
        Question.reviewed == True,  # noqa: E712
    )
    pool = [q for q in base_query.all() if q.question_id not in done_ids]
    if not pool:
        pool = base_query.all()

    target_elo = 1400.0
    if x_user_id and concept_ids:
        elos = [_mastery_or_default(db, x_user_id, cid)[0] for cid in concept_ids]
        target_elo = sum(elos) / len(elos)
    target_elo += {"easy": -150, "challenge": 150, "hard": 150}.get(req.difficulty, 0)

    pool.sort(key=lambda q: abs((q.item_elo or 1500) - target_elo))
    selected = pool[: req.num_questions]

    result = []
    for q in selected:
        c = db.query(Concept).filter(Concept.concept_id == q.concept_id).first()
        elo_val = target_elo
        if x_user_id and c:
            elo_val, _ = _mastery_or_default(db, x_user_id, c.concept_id)
        result.append({
            "c": {"id": c.concept_id, "name": c.name, "elo": round(elo_val), "slides": [q.source_slide]},
            "item": {
                "q": q.stem,
                "opts": q.options,
                "ans": q.answer_idx,
                "explanation": q.explanation,
                "question_id": q.question_id,
            },
        })
    return result
