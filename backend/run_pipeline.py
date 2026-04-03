from csv_loader import load_csv, load_teacher_answers
from cluster_processor import group_by_cluster
from grading.scoring_engine import grade_cluster
from rubric_generator import generate_rubric
import json
import os

data = load_csv("final_clustered_grades (1).csv")
teacher_answers = load_teacher_answers("Answer_Key_Q1_Q2.csv")

clusters = group_by_cluster(data)

final_output = []

for cluster_id, answers in clusters.items():

    # 🔥 use question_id instead of question text
    qid = answers[0].get("question_id", "Q1")

    teacher_data = teacher_answers.get(qid, {})

    rubric = generate_rubric(teacher_data)

    print("\nCLUSTER:", cluster_id, "| QUESTION:", qid)
    print("RUBRIC:", rubric)

    cluster_payload = {
        "cluster_id": cluster_id,
        "answers": answers,
        "rubric": rubric
    }

    result = grade_cluster(cluster_payload)
    final_output.append(result)

# save
output_path = os.path.join(os.path.dirname(__file__), "output.json")

with open(output_path, "w") as f:
    json.dump(final_output, f, indent=2)

print("\n✅ Output saved at:", output_path)
