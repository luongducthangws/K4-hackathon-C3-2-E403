"""
Buoc 2 (muc 6, master doc): sinh concept map tu text da trich (slides.json).

Concept map o day duoc tac gia hoa truc tiep (Claude doc toan bo slides.json
cua ca 2 bai, gom cum slide theo mach noi dung that su) - dung vai tro
"Content factory" trong kien truc 2 tang o muc 3: chay offline 1 lan luc
seed, khong phai runtime.

Script nay CHI lam viec validate + lap rap, khong tu suy luan cluster:
- Kiem tra moi cum slide_start<=slide_end, nam trong pham vi n_slides that
- Kiem tra khong overlap giua cac concept trong cung 1 lecture
- Kiem tra prereq_id (neu co) tro ve concept_id da ton tai
- Ghi concepts.json + slide_concept.json vao dung thu muc tung bai, kem
  seed.sql tong hop o goc, theo dung schema muc 5
- Ghi de lecture.json cua tung bai voi summary do LLM viet (thay placeholder
  noi title)

Output:
  data/processed/{lecture_id}/concepts.json
  data/processed/{lecture_id}/slide_concept.json
  data/processed/{lecture_id}/lecture.json (cap nhat summary)
  data/processed/seed.sql (tong hop tat ca bai, dung de seed DB 1 lan)
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


LECTURE_SUMMARIES = {
    "d1-ai-llm-foundation": (
        "Bài giảng mở ra bức tranh AI dạng tầng: AI bao trùm ML, Deep "
        "Learning, Generative AI, với LLM là tầng nền. Điểm qua lịch sử 70 "
        "năm AI (expert system 1980, ImageNet 2009, Transformer 2017, "
        "ChatGPT 2022) rồi đi sâu vào cơ chế LLM: token hóa, context "
        "window, attention, tham số và scaling law (dense vs MoE), quy "
        "trình huấn luyện pretraining → SFT → RLHF/DPO → reasoning. Nêu rõ "
        "giới hạn bẩm sinh của LLM (knowledge cutoff, hallucination, học "
        "vẹt đường tắt) và cách Chain-of-Thought cải thiện suy luận. Kết "
        "bài bằng bước từ LLM lên Agent (4 cấp độ tự chủ), cách chọn model "
        "theo tầng chi phí, và kỹ thuật prompt cơ bản (4 lớp prompt, "
        "temperature/top_p)."
    ),
    "d2-xac-dinh-bai-toan": (
        "Bài giảng dạy quy trình biến một yêu cầu AI mơ hồ thành Problem "
        "Statement rõ ràng, dùng khung Double Diamond (Discover/Define/"
        "Develop/Deliver) và Google PAIR. Học viên học cách tìm đúng bài "
        "toán (4 lens, tránh anti-pattern solution-first), định lượng hóa "
        "điểm đau (baseline/target/measurement), rồi đi qua 3 bước PAIR: "
        "(1) AI có thật sự cần thiết không, (2) Automate hay Augment và "
        "chọn cấp độ giải pháp Rule/Workflow/Agent, (3) thiết kế reward "
        "function và đánh đổi precision/recall. Kết thúc bằng cách viết "
        "Problem Statement đầy đủ 9 trường và ra quyết định Go / Not Yet / "
        "No-Go dựa trên lập luận chứ không phải thiên kiến công nghệ."
    ),
}

CONCEPT_MAPS = {
    "d1-ai-llm-foundation": [
        {"concept_id": "d1-c01", "name": "Bức tranh AI: các tầng AI & ba nhóm AI (Discriminative/Generative/Agentic)", "slide_start": 3, "slide_end": 4, "prereq_id": None},
        {"concept_id": "d1-c02", "name": "Lịch sử AI 70 năm: hệ chuyên gia, ImageNet, Transformer, ChatGPT", "slide_start": 5, "slide_end": 9, "prereq_id": "d1-c01"},
        {"concept_id": "d1-c03", "name": "LLM là gì & cơ chế sinh văn bản (next-token prediction)", "slide_start": 10, "slide_end": 12, "prereq_id": "d1-c02"},
        {"concept_id": "d1-c04", "name": "Token hóa (tokenization)", "slide_start": 13, "slide_end": 13, "prereq_id": "d1-c03"},
        {"concept_id": "d1-c05", "name": "Context window", "slide_start": 14, "slide_end": 14, "prereq_id": "d1-c04"},
        {"concept_id": "d1-c06", "name": "Cơ chế Attention", "slide_start": 15, "slide_end": 16, "prereq_id": "d1-c05"},
        {"concept_id": "d1-c07", "name": "Tham số mô hình & scaling law (dense vs MoE)", "slide_start": 17, "slide_end": 17, "prereq_id": "d1-c03"},
        {"concept_id": "d1-c08", "name": "Quy trình huấn luyện LLM: pretraining, SFT, RLHF/DPO", "slide_start": 18, "slide_end": 19, "prereq_id": "d1-c07"},
        {"concept_id": "d1-c09", "name": "Giới hạn của LLM: knowledge cutoff, hallucination, context có hạn", "slide_start": 20, "slide_end": 20, "prereq_id": "d1-c08"},
        {"concept_id": "d1-c10", "name": "Học vẹt đường tắt (spurious cues)", "slide_start": 21, "slide_end": 21, "prereq_id": "d1-c09"},
        {"concept_id": "d1-c11", "name": "Chain-of-Thought reasoning", "slide_start": 22, "slide_end": 22, "prereq_id": "d1-c09"},
        {"concept_id": "d1-c12", "name": "Từ LLM đến Agent: 4 cấp độ & giải phẫu agent", "slide_start": 23, "slide_end": 24, "prereq_id": "d1-c03"},
        {"concept_id": "d1-c13", "name": "Chi phí token & chọn model theo tầng", "slide_start": 25, "slide_end": 27, "prereq_id": "d1-c04"},
        {"concept_id": "d1-c14", "name": "Kỹ thuật prompt: 4 lớp prompt & núm vặn temperature/top_p", "slide_start": 28, "slide_end": 29, "prereq_id": "d1-c06"},
    ],
    "d2-xac-dinh-bai-toan": [
        {"concept_id": "d2-c01", "name": "Problem Discovery: mô hình Double Diamond", "slide_start": 3, "slide_end": 4, "prereq_id": None},
        {"concept_id": "d2-c02", "name": "Case study: khởi nguồn từ bài toán (Cursor, Artifact, NotebookLM)", "slide_start": 5, "slide_end": 5, "prereq_id": "d2-c01"},
        {"concept_id": "d2-c03", "name": "Tìm bài toán AI: bốn lens & sai lầm thường gặp (anti-pattern)", "slide_start": 6, "slide_end": 7, "prereq_id": "d2-c02"},
        {"concept_id": "d2-c04", "name": "Reframe câu hỏi PAIR & Quick Problem Card", "slide_start": 8, "slide_end": 9, "prereq_id": "d2-c03"},
        {"concept_id": "d2-c05", "name": "Khai thác bài toán & định lượng hóa (baseline/target/measurement)", "slide_start": 10, "slide_end": 11, "prereq_id": "d2-c04"},
        {"concept_id": "d2-c06", "name": "Thiết lập chỉ số: Output metric & Input metric", "slide_start": 12, "slide_end": 12, "prereq_id": "d2-c05"},
        {"concept_id": "d2-c07", "name": "PAIR bước 1: AI có thật sự cần thiết? (AI probably better/not better)", "slide_start": 13, "slide_end": 15, "prereq_id": "d2-c06"},
        {"concept_id": "d2-c08", "name": "Kiến trúc hệ thống AI (Model+Context+Planning+Tools) & Automate vs Augment", "slide_start": 16, "slide_end": 17, "prereq_id": "d2-c07"},
        {"concept_id": "d2-c09", "name": "Ba mức giải pháp: Rule / Workflow / Agent", "slide_start": 18, "slide_end": 19, "prereq_id": "d2-c08"},
        {"concept_id": "d2-c10", "name": "Workflow patterns & cây quyết định chọn cấp độ giải pháp", "slide_start": 20, "slide_end": 21, "prereq_id": "d2-c09"},
        {"concept_id": "d2-c11", "name": "Reward function (TP/TN/FP/FN) & đánh đổi Precision-Recall", "slide_start": 22, "slide_end": 23, "prereq_id": "d2-c08"},
        {"concept_id": "d2-c12", "name": "Viết tiêu chí thành công hành động được", "slide_start": 24, "slide_end": 24, "prereq_id": "d2-c11"},
        {"concept_id": "d2-c13", "name": "Khoảng cách Demo đến Production & Eval Plan", "slide_start": 25, "slide_end": 26, "prereq_id": "d2-c12"},
        {"concept_id": "d2-c14", "name": "Problem Statement đầy đủ 9 trường & quyết định Go/Not Yet/No-Go", "slide_start": 27, "slide_end": 28, "prereq_id": "d2-c13"},
        {"concept_id": "d2-c15", "name": "Recap: sáu nguyên tắc cốt lõi", "slide_start": 29, "slide_end": 29, "prereq_id": "d2-c14"},
    ],
}


def validate(lectures: list, slides: list):
    n_slides_by_lecture = {l["lecture_id"]: l["n_slides"] for l in lectures}
    errors = []

    for lecture_id, concepts in CONCEPT_MAPS.items():
        if lecture_id not in n_slides_by_lecture:
            errors.append(f"[{lecture_id}] khong co trong lectures.json")
            continue
        n_slides = n_slides_by_lecture[lecture_id]
        known_ids = {c["concept_id"] for c in concepts}

        ranges = []
        for c in concepts:
            if not (1 <= c["slide_start"] <= c["slide_end"] <= n_slides):
                errors.append(
                    f"[{lecture_id}/{c['concept_id']}] slide range "
                    f"{c['slide_start']}-{c['slide_end']} vuot ngoai 1..{n_slides}"
                )
            if c["prereq_id"] is not None and c["prereq_id"] not in known_ids:
                errors.append(
                    f"[{lecture_id}/{c['concept_id']}] prereq_id "
                    f"'{c['prereq_id']}' khong ton tai trong cung bai"
                )
            ranges.append((c["slide_start"], c["slide_end"], c["concept_id"]))

        ranges.sort()
        for (s1, e1, id1), (s2, e2, id2) in zip(ranges, ranges[1:]):
            if s2 <= e1:
                errors.append(
                    f"[{lecture_id}] concept {id1} ({s1}-{e1}) va {id2} "
                    f"({s2}-{e2}) bi chong lap slide"
                )

        n_concepts = len(concepts)
        if not (10 <= n_concepts <= 15):
            errors.append(
                f"[{lecture_id}] co {n_concepts} concept, ngoai khoang "
                f"khuyen nghi 10-15 (muc 6 master doc)"
            )

    return errors


def sql_escape(s: str) -> str:
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"


def build_seed_sql(lectures, slides, concepts, slide_concepts) -> str:
    lines = ["-- Seed data sinh tu scripts/extract_slides.py + build_concept_map.py", ""]

    lines.append("-- ============ lectures ============")
    for l in lectures:
        lines.append(
            "INSERT INTO lectures (lecture_id, title, n_slides, summary) VALUES "
            f"({sql_escape(l['lecture_id'])}, {sql_escape(l['title'])}, "
            f"{l['n_slides']}, {sql_escape(l['summary'])});"
        )
    lines.append("")

    lines.append("-- ============ slides ============")
    for s in slides:
        lines.append(
            "INSERT INTO slides (lecture_id, slide_no, title, body_text, image_url) VALUES "
            f"({sql_escape(s['lecture_id'])}, {s['slide_no']}, {sql_escape(s['title'])}, "
            f"{sql_escape(s['body_text'])}, {sql_escape(s['image_url'])});"
        )
    lines.append("")

    lines.append("-- ============ concepts ============")
    lines.append("-- Insert theo thu tu topo (prereq truoc) de FK khong loi.")
    for lecture_id, concept_list in concepts.items():
        for c in concept_list:
            lines.append(
                "INSERT INTO concepts (concept_id, lecture_id, name, prereq_id) VALUES "
                f"({sql_escape(c['concept_id'])}, {sql_escape(lecture_id)}, "
                f"{sql_escape(c['name'])}, {sql_escape(c['prereq_id'])});"
            )
    lines.append("")

    lines.append("-- ============ slide_concept ============")
    for lecture_id, sc_list in slide_concepts.items():
        for sc in sc_list:
            lines.append(
                "INSERT INTO slide_concept (lecture_id, concept_id, slide_start, slide_end) VALUES "
                f"({sql_escape(lecture_id)}, {sql_escape(sc['concept_id'])}, "
                f"{sc['slide_start']}, {sc['slide_end']});"
            )

    return "\n".join(lines) + "\n"


def main():
    lecture_ids = list(CONCEPT_MAPS.keys())
    lectures = []
    slides = []
    for lecture_id in lecture_ids:
        lecture_dir = PROCESSED / lecture_id
        lectures.append(json.loads((lecture_dir / "lecture.json").read_text(encoding="utf-8")))
        slides.extend(json.loads((lecture_dir / "slides.json").read_text(encoding="utf-8")))

    errors = validate(lectures, slides)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("Validation OK: khong overlap, slide range hop le, prereq_id hop le, so concept trong 10-15.")

    all_concepts = []
    all_slide_concepts = []
    for lecture in lectures:
        lecture_id = lecture["lecture_id"]
        if lecture_id in LECTURE_SUMMARIES:
            lecture["summary"] = LECTURE_SUMMARIES[lecture_id]
        lecture_dir = PROCESSED / lecture_id
        (lecture_dir / "lecture.json").write_text(
            json.dumps(lecture, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        concept_list = CONCEPT_MAPS[lecture_id]
        lecture_concepts = [
            {
                "concept_id": c["concept_id"],
                "lecture_id": lecture_id,
                "name": c["name"],
                "prereq_id": c["prereq_id"],
            }
            for c in concept_list
        ]
        lecture_slide_concepts = [
            {
                "lecture_id": lecture_id,
                "concept_id": c["concept_id"],
                "slide_start": c["slide_start"],
                "slide_end": c["slide_end"],
            }
            for c in concept_list
        ]
        (lecture_dir / "concepts.json").write_text(
            json.dumps(lecture_concepts, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (lecture_dir / "slide_concept.json").write_text(
            json.dumps(lecture_slide_concepts, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        all_concepts.extend(lecture_concepts)
        all_slide_concepts.extend(lecture_slide_concepts)

    seed_sql = build_seed_sql(lectures, slides, CONCEPT_MAPS, {
        lecture_id: [
            {"concept_id": c["concept_id"], "slide_start": c["slide_start"], "slide_end": c["slide_end"]}
            for c in concept_list
        ]
        for lecture_id, concept_list in CONCEPT_MAPS.items()
    })
    (PROCESSED / "seed.sql").write_text(seed_sql, encoding="utf-8")

    for lecture_id in lecture_ids:
        print(f"Ghi ra: {PROCESSED / lecture_id}/lecture.json (da cap nhat summary)")
        print(f"Ghi ra: {PROCESSED / lecture_id}/concepts.json, slide_concept.json")
    print(f"Tong: {len(all_concepts)} concept, {len(all_slide_concepts)} dong slide_concept")
    print(f"Ghi ra: {PROCESSED / 'seed.sql'} (tong hop tat ca bai)")


if __name__ == "__main__":
    main()
