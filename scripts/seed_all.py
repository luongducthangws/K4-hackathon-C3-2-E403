import os
import sys
import json
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, SessionLocal, Base
from backend.models import Lecture, Slide, Concept, SlideConcept, Question

def seed_all():
    print("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")

    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        print(f"\n--- Seeding data for: {folder_name} ---")

        # 1. Lecture
        lec_file = os.path.join(folder_path, "lecture.json")
        if os.path.exists(lec_file):
            with open(lec_file, "r", encoding="utf-8") as f:
                d = json.load(f)
                exists = db.query(Lecture).filter(Lecture.lecture_id == d["lecture_id"]).first()
                if not exists:
                    lec = Lecture(
                        lecture_id=d["lecture_id"],
                        title=d.get("title", ""),
                        n_slides=d.get("n_slides", 0),
                        summary=d.get("summary", "")
                    )
                    db.add(lec)
                    db.commit()
                    print(f"Added Lecture: {d['lecture_id']}")
                else:
                    print(f"Lecture {d['lecture_id']} already exists.")

        # 2. Slides
        slides_file = os.path.join(folder_path, "slides.json")
        if os.path.exists(slides_file):
            with open(slides_file, "r", encoding="utf-8") as f:
                slides_data = json.load(f)
                added_count = 0
                for s in slides_data:
                    exists = db.query(Slide).filter(
                        Slide.lecture_id == s["lecture_id"],
                        Slide.slide_no == s["slide_no"]
                    ).first()
                    if not exists:
                        slide = Slide(
                            lecture_id=s["lecture_id"],
                            slide_no=s["slide_no"],
                            title=s.get("title", ""),
                            body_text=s.get("body_text", ""),
                            image_url=s.get("image_url", "")
                        )
                        db.add(slide)
                        added_count += 1
                db.commit()
                print(f"Added {added_count} Slides for {folder_name}")

        # 3. Concepts
        concepts_file = os.path.join(folder_path, "concepts.json")
        if os.path.exists(concepts_file):
            with open(concepts_file, "r", encoding="utf-8") as f:
                concepts_data = json.load(f)
                added_count = 0
                for c in concepts_data:
                    exists = db.query(Concept).filter(Concept.concept_id == c["concept_id"]).first()
                    if not exists:
                        concept = Concept(
                            concept_id=c["concept_id"],
                            lecture_id=c["lecture_id"],
                            name=c["name"],
                            prereq_id=c.get("prereq_id")
                        )
                        db.add(concept)
                        added_count += 1
                db.commit()
                print(f"Added {added_count} Concepts for {folder_name}")

        # 4. SlideConcepts
        sc_file = os.path.join(folder_path, "slide_concept.json")
        if os.path.exists(sc_file):
            with open(sc_file, "r", encoding="utf-8") as f:
                sc_data = json.load(f)
                added_count = 0
                for sc in sc_data:
                    exists = db.query(SlideConcept).filter(
                        SlideConcept.lecture_id == sc["lecture_id"],
                        SlideConcept.concept_id == sc["concept_id"],
                        SlideConcept.slide_start == sc["slide_start"]
                    ).first()
                    if not exists:
                        item = SlideConcept(
                            lecture_id=sc["lecture_id"],
                            concept_id=sc["concept_id"],
                            slide_start=sc["slide_start"],
                            slide_end=sc.get("slide_end", sc["slide_start"])
                        )
                        db.add(item)
                        added_count += 1
                db.commit()
                print(f"Added {added_count} SlideConcepts for {folder_name}")

        # 5. Questions
        q_file = os.path.join(folder_path, "questions.json")
        if os.path.exists(q_file):
            with open(q_file, "r", encoding="utf-8") as f:
                q_data = json.load(f)
                added_count = 0
                for q in q_data:
                    exists = db.query(Question).filter(
                        Question.concept_id == q["concept_id"],
                        Question.stem == q["stem"]
                    ).first()
                    if not exists:
                        question = Question(
                            concept_id=q["concept_id"],
                            stem=q["stem"],
                            options=q["options"],
                            answer_idx=q["answer_idx"],
                            explanation=q.get("explanation", ""),
                            source_slide=q.get("source_slide", 0),
                            item_elo=q.get("item_elo", 1500),
                            reviewed=q.get("reviewed", True)
                        )
                        db.add(question)
                        added_count += 1
                db.commit()
                print(f"Added {added_count} Questions for {folder_name}")

    db.close()
    print("\nSuccessfully seeded all data into PostgreSQL!")

if __name__ == "__main__":
    seed_all()
