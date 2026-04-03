from grading.regex_parser import extract_math_expressions
from grading.math_validator import validate_equation
from collections import Counter
import re
import time
from difflib import SequenceMatcher


def grade_cluster(cluster_payload):
    start_time = time.time()
    results = []
    rubric = cluster_payload["rubric"]

    for ans in cluster_payload["answers"]:
        student_text = ans["raw_text"].strip().replace("\n", " ")

        # -----------------------------
        # EMPTY CHECK
        # -----------------------------
        if not student_text or not re.search(r'[a-zA-Z]', student_text):
            results.append({
                "student_id": ans["student_id"],
                "score": 0,
                "confidence": 0,
                "feedback": ["Invalid or empty answer"]
            })
            continue

        q_type = rubric.get("type", "theory")

        # =====================================================
        # THEORY MODE
        # =====================================================
        if q_type == "theory":
            required = rubric.get("required_elements", [])

            if not required:
                final_score = 0.3
            else:
                total_score = 0

                for concept in required:
                    similarity = SequenceMatcher(
                        None,
                        concept.lower(),
                        student_text.lower()
                    ).ratio()

                    if similarity > 0.7:
                        total_score += 1.0
                    elif similarity > 0.5:
                        total_score += 0.7
                    elif similarity > 0.3:
                        total_score += 0.4
                    else:
                        total_score += 0

                final_score = total_score / len(required)

        # =====================================================
        # MATH MODE
        # =====================================================
        elif q_type == "math":
            student_math = extract_math_expressions(student_text)
            correct_eq = rubric.get("equation")

            if not student_math:
                final_score = 0
            else:
                correct = any(
                    validate_equation(expr, correct_eq)
                    for expr in student_math
                )
                final_score = 1.0 if correct else 0.5

        # =====================================================
        # LANGUAGE MODE
        # =====================================================
        elif q_type == "language":
            similarity = SequenceMatcher(
                None,
                student_text.lower(),
                rubric.get("model_answer", "").lower()
            ).ratio()

            final_score = min(1.0, similarity * 1.2)

        else:
            final_score = 0

        # -----------------------------
        # FEEDBACK
        # -----------------------------
        if final_score >= 0.7:
            feedback = ["Excellent answer"]
        elif final_score >= 0.5:
            feedback = ["Good answer"]
        elif final_score >= 0.25:
            feedback = ["Partially correct answer"]
        else:
            feedback = ["Needs improvement"]

        results.append({
            "student_id": ans["student_id"],
            "score": round(final_score, 2),
            "confidence": round(final_score, 2),
            "feedback": feedback
        })

    # -----------------------------
    # ANALYTICS
    # -----------------------------
    avg_score = sum(r["score"] for r in results) / len(results)

    all_feedback = []
    for r in results:
        all_feedback.extend(r["feedback"])

    top_issues = [
        issue for issue, _ in Counter(all_feedback).most_common(3)
    ]

    return {
        "cluster_id": cluster_payload["cluster_id"],
        "cluster_size": len(results),
        "avg_score": round(avg_score, 2),
        "top_issues": top_issues,
        "processing_time": round(time.time() - start_time, 2),
        "results": results
    }
