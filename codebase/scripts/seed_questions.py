import os
import sys
import json
from sqlalchemy.orm import Session

# Add parent directory to sys.path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, SessionLocal, Base
from backend.models import Concept, Question

def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_data_dir = os.path.join(parent_dir, "data", "processed")
    if not os.path.exists(base_data_dir):
        grandparent_dir = os.path.dirname(parent_dir)
        base_data_dir = os.path.join(grandparent_dir, "data", "processed")

    
    for folder_name in os.listdir(base_data_dir):
        data_dir = os.path.join(base_data_dir, folder_name)
        if not os.path.isdir(data_dir):
            continue
            
        concepts_file = os.path.join(data_dir, "concepts.json")
        questions_file = os.path.join(data_dir, "questions.json")
        
        # 1. Seed Concepts
        print(f"Seeding concepts from {folder_name}...")
        if os.path.exists(concepts_file):
            with open(concepts_file, "r", encoding="utf-8") as f:
                concepts_data = json.load(f)
                for c_data in concepts_data:
                    # Check if exists
                    exists = db.query(Concept).filter(Concept.concept_id == c_data["concept_id"]).first()
                    if not exists:
                        concept = Concept(
                            concept_id=c_data["concept_id"],
                            lecture_id=c_data["lecture_id"],
                            name=c_data["name"],
                            prereq_id=c_data.get("prereq_id")
                        )
                        db.add(concept)
                db.commit()
                print(f"Loaded concepts from {concepts_file}")
                
        # 2. Seed Questions
        print(f"Seeding questions from {folder_name}...")
        if os.path.exists(questions_file):
            with open(questions_file, "r", encoding="utf-8") as f:
                questions_data = json.load(f)
                for q_data in questions_data:
                    # Make sure the concept exists
                    concept = db.query(Concept).filter(Concept.concept_id == q_data["concept_id"]).first()
                    if concept:
                        # Check if question already seeded
                        exists = db.query(Question).filter(Question.concept_id == q_data["concept_id"], Question.stem == q_data["stem"]).first()
                        if not exists:
                            question = Question(
                                concept_id=q_data["concept_id"],
                                stem=q_data["stem"],
                                options=q_data["options"],
                                answer_idx=q_data["answer_idx"],
                                explanation=q_data.get("explanation", ""),
                                source_slide=q_data.get("source_slide", 0),
                                item_elo=q_data.get("item_elo", 1500),
                                reviewed=q_data.get("reviewed", True),
                            )
                            db.add(question)
                db.commit()
                print(f"Loaded questions from {questions_file}")
                
    db.close()
    print("Done seeding questions!")

if __name__ == "__main__":
    main()
