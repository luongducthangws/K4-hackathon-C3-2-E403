import os
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from .database import SessionLocal
from .lecture_alias import resolve_lecture_id
from .models import Concept, Lecture, Slide, SlideConcept

load_dotenv()
if "GOOGLE_API_KEY" not in os.environ and "GEMINI_API_KEY" in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

DEFAULT_REJECTION = "Xin lỗi, mình chỉ có thể trả lời các câu hỏi liên quan đến bài học. Bạn có thể nói rõ hơn được không?"


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    lecture_id: str
    context: str
    concept_ids: list[str]
    is_relevant: bool


import re


def route_node(state: AgentState):
    """Call 1: định tuyến câu hỏi tới 1-3 concept_id, hoặc từ chối nếu ngoài đề."""
    real_lecture_id = resolve_lecture_id(state.get("lecture_id", "day01"))

    db = SessionLocal()
    try:
        concepts = db.query(Concept).filter(Concept.lecture_id == real_lecture_id).all()
        concept_items = []
        for c in concepts:
            sc = db.query(SlideConcept).filter(
                SlideConcept.lecture_id == real_lecture_id,
                SlideConcept.concept_id == c.concept_id,
            ).first()
            slides_str = f" (Slide {sc.slide_start}-{sc.slide_end})" if (sc and sc.slide_end and sc.slide_end != sc.slide_start) else (f" (Slide {sc.slide_start})" if sc else "")
            concept_items.append(f"- {c.concept_id}: {c.name}{slides_str}")
    finally:
        db.close()

    user_msg = state["messages"][-1].content if state.get("messages") else ""
    explicit_slides = re.findall(r"(?:slide|trang)\s*#?\s*([0-9]+)", user_msg, re.IGNORECASE)

    concept_list = "\n".join(concept_items)
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0)

    sys_prompt = f"""Bạn là bộ định tuyến cho chatbot hỏi đáp bài giảng.
Danh sách concept và vị trí slide tương ứng của bài giảng đang mở:
{concept_list}

Đọc câu hỏi mới nhất của học viên và lịch sử hội thoại. Xác định:
1. RELEVANT: câu hỏi liên quan tới bài giảng/lĩnh vực chuyên môn hoặc hỏi về slide cụ thể — chọn tối đa 3 concept_id liên quan nhất từ danh sách trên (đúng id, cách nhau bằng dấu phẩy). Nếu không concept nào khớp rõ nhưng câu hỏi vẫn thuộc bài giảng (hoặc hỏi về slide cụ thể), hãy chọn concept gần nhất hoặc để trống danh sách.
2. IRRELEVANT: nói chuyện phiếm ngoài đề, hoặc spam không liên quan tới bài học.

Output ĐÚNG một trong hai format:
RELEVANT: <concept_id1,concept_id2,...>
IRRELEVANT: <câu trả lời lịch sự bằng tiếng Việt — từ chối và hướng học viên về bài học>
"""

    messages = [SystemMessage(content=sys_prompt)] + state["messages"]
    response = llm.invoke(messages)

    if isinstance(response.content, list):
        content = "".join(item.get("text", "") for item in response.content if isinstance(item, dict) and "text" in item)
    else:
        content = str(response.content)
    content = content.strip()

    if content.startswith("RELEVANT:") or explicit_slides:
        raw_ids = content.replace("RELEVANT:", "").strip() if content.startswith("RELEVANT:") else ""
        concept_ids = [c.strip() for c in raw_ids.split(",") if c.strip()]
        return {"is_relevant": True, "concept_ids": concept_ids}

    rejection_text = content.replace("IRRELEVANT:", "").strip() or DEFAULT_REJECTION
    return {"is_relevant": False, "messages": [AIMessage(content=rejection_text)]}


def retrieve_node(state: AgentState):
    """Call DB thuần: lấy cụm slide của các concept đã định tuyến + slide được hỏi trực tiếp."""
    real_lecture_id = resolve_lecture_id(state.get("lecture_id", "day01"))
    concept_ids = state.get("concept_ids") or []

    user_msg = state["messages"][-1].content if state.get("messages") else ""
    explicit_slides = re.findall(r"(?:slide|trang)\s*#?\s*([0-9]+)", user_msg, re.IGNORECASE)

    db = SessionLocal()
    try:
        lecture = db.query(Lecture).filter(Lecture.lecture_id == real_lecture_id).first()
        summary = lecture.summary if lecture else ""

        slide_nos: set[int] = set()
        
        # Explicit slide numbers from user prompt
        for s_str in explicit_slides:
            try:
                s_num = int(s_str)
                slide_nos.update(range(max(1, s_num - 1), s_num + 2))
            except ValueError:
                pass

        if concept_ids:
            ranges = db.query(SlideConcept).filter(
                SlideConcept.lecture_id == real_lecture_id,
                SlideConcept.concept_id.in_(concept_ids),
            ).all()
            for r in ranges:
                start = max(1, r.slide_start - 1)
                end = (r.slide_end or r.slide_start) + 1
                slide_nos.update(range(start, end + 1))

        parts = []
        if summary:
            parts.append(f"[Tóm tắt bài giảng]\n{summary}")

        if slide_nos:
            slides = db.query(Slide).filter(
                Slide.lecture_id == real_lecture_id,
                Slide.slide_no.in_(sorted(slide_nos)),
            ).order_by(Slide.slide_no).all()
            for s in slides:
                if s.body_text:
                    parts.append(f"[Slide {s.slide_no} - {s.title or ''}]\n{s.body_text}")
        else:
            # Fallback: load all slides if no specific slide_nos identified
            slides = db.query(Slide).filter(
                Slide.lecture_id == real_lecture_id
            ).order_by(Slide.slide_no).all()
            for s in slides:
                if s.body_text:
                    parts.append(f"[Slide {s.slide_no} - {s.title or ''}]\n{s.body_text}")

        return {"context": "\n---\n".join(parts)}
    finally:
        db.close()


def route_after_routing(state: AgentState) -> Literal["retrieve", "__end__"]:
    if state.get("is_relevant", False):
        return "retrieve"
    return "__end__"


workflow = StateGraph(AgentState)
workflow.add_node("route", route_node)
workflow.add_node("retrieve", retrieve_node)

workflow.add_edge(START, "route")
workflow.add_conditional_edges("route", route_after_routing)
workflow.add_edge("retrieve", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
