from csv_loader import load_csv
from cluster_processor import group_by_cluster
from grading.scoring_engine import grade_cluster
from rubric_generator import generate_rubric
import json

# ✅ Load YOUR actual CSV
data = load_csv("final_clustered_grades.csv")

# Group into clusters
clusters = group_by_cluster(data)

final_output = []

# Process each cluster
for cluster_id, answers in clusters.items():

    # 🔥 get reference answer (same for cluster)
    reference_answer = answers[0].get("reference_answer", "")

    rubric = generate_rubric(reference_answer)

    cluster_payload = {
        "cluster_id": cluster_id,
        "answers": answers,
        "rubric": rubric
    }

    result = grade_cluster(cluster_payload)
    final_output.append(result)

# ✅ Pretty print output
print(json.dumps(final_output, indent=2))

# 🔥 OPTIONAL: save output to file
with open("output.json", "w") as f:
    json.dump(final_output, f, indent=2)
