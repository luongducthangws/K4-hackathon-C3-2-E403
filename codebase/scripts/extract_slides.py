"""
Buoc 1 (muc 7, master doc): trich text tu slide PDF bang PyMuPDF.
Chien luoc lai: doc text layer truoc, dem ky tu moi trang; trang nao duoi
nguong (50 ky tu) thi danh dau can_fallback=True (VLM/OCR) thay vi tu dong
render anh - quyet dinh do nguoi duyet.

Output: mot thu muc rieng cho moi bai giang, de de xem tung bai:
  data/processed/{lecture_id}/lecture.json
  data/processed/{lecture_id}/slides.json
Khop schema bang `lectures` / `slides` o muc 5 cua master doc.
"""
import json
import sys
from pathlib import Path

import fitz  # PyMuPDF

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "data").exists() and Path(__file__).resolve().parents[2].joinpath("data").exists():
    ROOT = Path(__file__).resolve().parents[2]
SLIDES_DIR = ROOT / "data" / "vlearn-pack" / "slides"
OUT_DIR = ROOT / "data" / "processed"

OUT_DIR.mkdir(parents=True, exist_ok=True)

THIN_TEXT_THRESHOLD = 50  # ky tu; duoi nguong nay -> fallback VLM/OCR

LECTURES = [
    {
        "lecture_id": "d1-ai-llm-foundation",
        "path": SLIDES_DIR / "d1-slide-hackathon.pdf",
        "title": "Day 1 - AI & LLM Foundation",
    },
    {
        "lecture_id": "d2-xac-dinh-bai-toan",
        "path": SLIDES_DIR / "d2-slide-hackathon.pdf",
        "title": "Day 2 - Xác định bài toán cho AI",
    },
]


def collect_boilerplate(doc, min_ratio: float = 0.5) -> set:
    """Cac dong lap lai tren >= min_ratio so trang (watermark/header/footer
    co dinh, VD 'AI IN ACTION - HACKATHON') -> loai khoi ung vien title."""
    counts: dict[str, int] = {}
    n_pages = doc.page_count
    for page in doc:
        seen_this_page = set()
        for block in page.get_text("dict").get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if text:
                        seen_this_page.add(text)
        for text in seen_this_page:
            counts[text] = counts.get(text, 0) + 1
    return {t for t, c in counts.items() if c / n_pages >= min_ratio}


def extract_title(page, boilerplate: set) -> str:
    """Doan title = dong co font-size lon nhat tren trang, sau khi loai
    watermark/header/footer lap lai tren nhieu trang (heuristic)."""
    data = page.get_text("dict")
    best_span = None
    for block in data.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text or text in boilerplate:
                    continue
                if best_span is None or span["size"] > best_span["size"]:
                    best_span = {"size": span["size"], "text": text}
    if best_span and len(best_span["text"]) <= 120:
        return best_span["text"]
    return ""


def clean_text(raw: str, boilerplate: set) -> str:
    lines = [ln.strip() for ln in raw.splitlines()]
    lines = [ln for ln in lines if ln and ln not in boilerplate]
    return "\n".join(lines)


def extract_pdf(lecture: dict) -> dict:
    doc = fitz.open(lecture["path"])
    boilerplate = collect_boilerplate(doc)
    slides = []
    thin_pages = []
    for i, page in enumerate(doc, start=1):
        raw = page.get_text()
        body = clean_text(raw, boilerplate)
        title = extract_title(page, boilerplate)
        char_count = len(body)
        can_fallback = char_count < THIN_TEXT_THRESHOLD
        if can_fallback:
            thin_pages.append(i)
        slides.append(
            {
                "lecture_id": lecture["lecture_id"],
                "slide_no": i,
                "title": title,
                "body_text": body,
                "char_count": char_count,
                "needs_fallback": can_fallback,
                "image_url": None,
            }
        )
    doc.close()
    return {"slides": slides, "thin_pages": thin_pages, "n_slides": len(slides)}


def make_summary(slides: list, max_chars: int = 900) -> str:
    """Tom tat tho: noi title cac slide lai, cat o max_chars (~200 token).
    Dung tam thoi lam input cho buoc sinh concept map / prompt chatbot;
    nen thay bang ban LLM tom tat that truoc khi seed production."""
    titles = [s["title"] for s in slides if s["title"]]
    joined = " | ".join(titles)
    return joined[:max_chars]


def main():
    n_lectures = 0
    n_slides_total = 0
    report_lines = []

    for lecture in LECTURES:
        result = extract_pdf(lecture)
        slides = result["slides"]
        summary = make_summary(slides)

        lecture_record = {
            "lecture_id": lecture["lecture_id"],
            "title": lecture["title"],
            "n_slides": result["n_slides"],
            "summary": summary,
        }

        lecture_dir = OUT_DIR / lecture["lecture_id"]
        lecture_dir.mkdir(parents=True, exist_ok=True)
        (lecture_dir / "lecture.json").write_text(
            json.dumps(lecture_record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (lecture_dir / "slides.json").write_text(
            json.dumps(slides, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        n_lectures += 1
        n_slides_total += len(slides)

        report_lines.append(f"## {lecture['lecture_id']} ({lecture['title']})")
        report_lines.append(f"- Tong so trang: {result['n_slides']}")
        report_lines.append(
            f"- Trang text mong (< {THIN_TEXT_THRESHOLD} ky tu, can fallback VLM/OCR): "
            f"{result['thin_pages'] if result['thin_pages'] else 'khong co'}"
        )
        char_counts = [s["char_count"] for s in slides]
        avg_chars = sum(char_counts) / len(char_counts) if char_counts else 0
        report_lines.append(f"- Trung binh ky tu/trang: {avg_chars:.0f}")
        report_lines.append(f"- File: data/processed/{lecture['lecture_id']}/lecture.json, slides.json")
        report_lines.append("")

    (OUT_DIR / "extract_report.md").write_text(
        "# Bao cao trich text slide (Buoc 1)\n\n" + "\n".join(report_lines),
        encoding="utf-8",
    )

    print(f"Da xu ly {n_lectures} bai giang, {n_slides_total} slide.")
    for lecture in LECTURES:
        print(f"Ghi ra: {OUT_DIR / lecture['lecture_id']}/lecture.json, slides.json")
    print(f"Bao cao: {OUT_DIR / 'extract_report.md'}")


if __name__ == "__main__":
    main()
