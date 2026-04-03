import json
from pathlib import Path


def load_cluster_reviews(review_path):
    review_path = Path(review_path)
    with open(review_path, "r", encoding="utf-8") as file:
        payload = json.load(file)
    return payload.get("reviews", payload)


def build_reviews_from_grading_output(grading_output_path, generated_review_path=None):
    grading_output_path = Path(grading_output_path)
    with open(grading_output_path, "r", encoding="utf-8") as file:
        grading_output = json.load(file)

    reviews = []
    for question_id, clusters in grading_output.items():
        for cluster in clusters:
            semantic = cluster.get("semantic_evaluation", {})
            suggested_marks = semantic.get("suggested_marks_display") or semantic.get("suggested_marks")
            reason = semantic.get("reason") or "Cluster review required."
            review = {
                "question_id": question_id,
                "cluster_id": int(cluster["cluster_id"]),
                "final_marks": suggested_marks or "manual review required",
                "teacher_note": reason,
                "source": "generated-from-output",
            }
            reviews.append(review)

    if generated_review_path:
        generated_review_path = Path(generated_review_path)
        generated_review_path.parent.mkdir(parents=True, exist_ok=True)
        with open(generated_review_path, "w", encoding="utf-8") as file:
            json.dump({"reviews": reviews}, file, indent=2)

    return reviews


def build_review_lookup(reviews):
    lookup = {}
    for review in reviews:
        key = (review["question_id"], int(review["cluster_id"]))
        lookup[key] = review
    return lookup
