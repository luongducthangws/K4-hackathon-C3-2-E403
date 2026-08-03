# -*- coding: utf-8 -*-
"""
Buoc 3 + 4 (muc 6, master doc): lap rap ngan hang cau hoi.

Noi dung cau hoi (stem/correct/distractors/explanation/source_slide) do
Claude tu doc slides.json cua tung bai va viet truc tiep trong
questions_d1_data.py / questions_d2_data.py - dung vai tro "Content
factory" (muc 3), khong goi API ngoai.

Script nay chi lam phan co the tu dong hoa (khong sinh noi dung):
- Rotate vi tri dap an dung trong 4 phuong an de tranh thien vi vi tri
  (neu luon dat dung o index 0 thi nguoi hoc doan mo cung trung cao)
- Tu kiem cau truc (Buoc 4 rut gon): 4 phuong an, khong trung lap noi
  dung, source_slide nam trong dai slide_start..slide_end cua dung
  concept, du 8-10 cau/concept
- Xuat questions.json cho tung bai + append vao seed.sql

Output:
  data/processed/{lecture_id}/questions.json
  data/processed/seed.sql (them phan INSERT INTO questions)
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "data").exists() and Path(__file__).resolve().parents[2].joinpath("data").exists():
    ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"


sys.path.insert(0, str(Path(__file__).resolve().parent))
from questions_d1_data import QUESTIONS_D1  # noqa: E402
from questions_d2_data import QUESTIONS_D2  # noqa: E402

QUESTION_BANKS = {
    "d1-ai-llm-foundation": QUESTIONS_D1,
    "d2-xac-dinh-bai-toan": QUESTIONS_D2,
}

MIN_QUESTIONS_PER_CONCEPT = 8
MAX_QUESTIONS_PER_CONCEPT = 10


def rotate_options(raw_q: dict, position: int) -> dict:
    """Dat dap an dung vao vi tri `position` (0-3) trong 4 phuong an,
    thay vi luon dat o dau - tranh thien vi vi tri khi hoc vien lam bai."""
    options = list(raw_q["distractors"])
    options.insert(position, raw_q["correct"])
    return {
        "stem": raw_q["stem"],
        "options": options,
        "answer_idx": position,
        "explanation": raw_q["explanation"],
        "source_slide": raw_q["source_slide"],
    }


def build_lecture_questions(lecture_id: str, bank: dict, slide_concept: list, n_slides: int) -> tuple:
    """Tra ve (questions, errors) cho 1 bai giang."""
    slide_range_by_concept = {
        sc["concept_id"]: (sc["slide_start"], sc["slide_end"]) for sc in slide_concept
    }
    errors = []
    questions = []

    for concept_id, raw_questions in bank.items():
        if concept_id not in slide_range_by_concept:
            errors.append(f"[{lecture_id}/{concept_id}] khong ton tai trong slide_concept.json")
            continue

        n = len(raw_questions)
        if not (MIN_QUESTIONS_PER_CONCEPT <= n <= MAX_QUESTIONS_PER_CONCEPT):
            errors.append(
                f"[{lecture_id}/{concept_id}] co {n} cau, ngoai khoang "
                f"{MIN_QUESTIONS_PER_CONCEPT}-{MAX_QUESTIONS_PER_CONCEPT}"
            )

        slide_start, slide_end = slide_range_by_concept[concept_id]
        seen_stems = set()

        for i, raw_q in enumerate(raw_questions):
            stem = raw_q["stem"]
            if stem in seen_stems:
                errors.append(f"[{lecture_id}/{concept_id}] cau hoi trung lap: {stem[:50]}...")
            seen_stems.add(stem)

            if len(raw_q["distractors"]) != 3:
                errors.append(
                    f"[{lecture_id}/{concept_id}] cau '{stem[:40]}...' phai co dung 3 distractor"
                )

            all_options = [raw_q["correct"]] + raw_q["distractors"]
            if len(set(all_options)) != len(all_options):
                errors.append(
                    f"[{lecture_id}/{concept_id}] cau '{stem[:40]}...' co phuong an trung lap noi dung"
                )

            src = raw_q["source_slide"]
            if not (slide_start <= src <= slide_end):
                errors.append(
                    f"[{lecture_id}/{concept_id}] cau '{stem[:40]}...' co source_slide={src} "
                    f"ngoai dai concept ({slide_start}-{slide_end})"
                )
            if not (1 <= src <= n_slides):
                errors.append(
                    f"[{lecture_id}/{concept_id}] source_slide={src} vuot ngoai 1..{n_slides}"
                )

            position = i % 4  # xoay vong tri dap an dung: 0,1,2,3,0,1,2,3...
            built = rotate_options(raw_q, position)
            built["concept_id"] = concept_id
            questions.append(built)

    return questions, errors


def sql_escape(s) -> str:
    if s is None:
        return "NULL"
    if isinstance(s, (int, float)):
        return str(s)
    return "'" + str(s).replace("'", "''") + "'"


def build_questions_sql(all_questions_by_lecture: dict) -> str:
    lines = ["-- ============ questions ============", "-- reviewed=FALSE mac dinh: cho nguoi duyet tay truoc khi dua vao quiz that."]
    for lecture_id, questions in all_questions_by_lecture.items():
        for q in questions:
            options_json = json.dumps(q["options"], ensure_ascii=False)
            lines.append(
                "INSERT INTO questions (concept_id, stem, options, answer_idx, explanation, "
                "item_elo, source_slide, reviewed) VALUES "
                f"({sql_escape(q['concept_id'])}, {sql_escape(q['stem'])}, "
                f"{sql_escape(options_json)}, {q['answer_idx']}, {sql_escape(q['explanation'])}, "
                f"1500, {q['source_slide']}, FALSE);"
            )
    return "\n".join(lines) + "\n"


def main():
    all_errors = []
    all_questions_by_lecture = {}

    for lecture_id, bank in QUESTION_BANKS.items():
        lecture_dir = PROCESSED / lecture_id
        lecture = json.loads((lecture_dir / "lecture.json").read_text(encoding="utf-8"))
        slide_concept = json.loads((lecture_dir / "slide_concept.json").read_text(encoding="utf-8"))
        concepts = json.loads((lecture_dir / "concepts.json").read_text(encoding="utf-8"))

        bank_concepts = set(bank.keys())
        map_concepts = {c["concept_id"] for c in concepts}
        missing = map_concepts - bank_concepts
        extra = bank_concepts - map_concepts
        if missing:
            all_errors.append(f"[{lecture_id}] thieu ngan hang cau hoi cho concept: {sorted(missing)}")
        if extra:
            all_errors.append(f"[{lecture_id}] co ngan hang cau hoi cho concept khong ton tai: {sorted(extra)}")

        questions, errors = build_lecture_questions(lecture_id, bank, slide_concept, lecture["n_slides"])
        all_errors.extend(errors)
        all_questions_by_lecture[lecture_id] = questions

    if all_errors:
        print("VALIDATION FAILED:")
        for e in all_errors:
            print(" -", e)
        sys.exit(1)

    total = sum(len(qs) for qs in all_questions_by_lecture.values())
    print(f"Validation OK: khong trung lap, source_slide hop le, 8-10 cau/concept. Tong {total} cau.")

    for lecture_id, questions in all_questions_by_lecture.items():
        lecture_dir = PROCESSED / lecture_id
        (lecture_dir / "questions.json").write_text(
            json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Ghi ra: {lecture_dir / 'questions.json'} ({len(questions)} cau)")

    questions_sql = build_questions_sql(all_questions_by_lecture)
    seed_path = PROCESSED / "seed.sql"
    existing = seed_path.read_text(encoding="utf-8") if seed_path.exists() else ""

    marker = "-- ============ questions ============"
    if marker in existing:
        existing = existing.split(marker)[0].rstrip() + "\n\n"
    else:
        existing = existing.rstrip() + "\n\n"

    seed_path.write_text(existing + questions_sql, encoding="utf-8")
    print(f"Cap nhat: {seed_path} (them {total} INSERT INTO questions)")


if __name__ == "__main__":
    main()
