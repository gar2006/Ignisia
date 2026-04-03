from grading.regex_parser import extract_math_expressions
from grading.math_validator import validate_equation
from collections import Counter
import re
import time
from difflib import SequenceMatcher


def highlight_keywords(text, keywords):
    for kw in keywords:
        text = re.sub(f"(?i)({kw})", r"<mark>\1</mark>", text)
    return text


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
        # 🔵 THEORY MODE (CONCEPT-BASED)
        # =====================================================
        if q_type == "theory":
            required = rubric.get("required_elements", [])
            concept_hits = 0

            for concept in required:
                words = concept.lower().split()

                matches = sum(1 for w in words if w in student_text.lower())

                if matches >= max(1, len(words) // 2):
                    concept_hits += 1

            final_score = concept_hits / len(required) if required else 0


        # =====================================================
        # 🔴 MATH MODE
        # =====================================================
        elif q_type == "math":
            student_math = extract_math_expressions(student_text)
            correct_eq = rubric.get("equation")

            math_correct = False

            if student_math:
                math_correct = any(
                    validate_equation(expr, correct_eq)
                    for expr in student_math
                )

            if math_correct:
                final_score = 1.0
            elif student_math:
                final_score = 0.5
            else:
                final_score = 0.0


        # =====================================================
        # 🟢 LANGUAGE MODE
        # =====================================================
        elif q_type == "language":
            similarity = SequenceMatcher(
                None,
                student_text.lower(),
                rubric.get("model_answer", "").lower()
            ).ratio()

            final_score = similarity


        else:
            final_score = 0


        # -----------------------------
        # FEEDBACK (CLEAN + STRONG)
        # -----------------------------
        feedback = []

        if final_score >= 0.8:
            feedback.append("Excellent answer")
        elif final_score >= 0.6:
            feedback.append("Good answer")
        elif final_score >= 0.3:
            feedback.append("Partially correct answer")
        else:
            feedback.append("Needs improvement")

        confidence = round(final_score, 2)

        results.append({
            "student_id": ans["student_id"],
            "score": round(final_score, 2),
            "confidence": confidence,
            "feedback": feedback
        })

    # -----------------------------
    # CLUSTER ANALYTICS
    # -----------------------------
    if not results:
        return {
            "cluster_id": cluster_payload["cluster_id"],
            "cluster_size": 0,
            "avg_score": 0,
            "top_issues": [],
            "processing_time": 0,
            "results": []
        }

    avg_score = sum(r["score"] for r in results) / len(results)

    all_feedback = []
    for r in results:
        all_feedback.extend(r["feedback"])

    top_issues = [
        issue for issue, _ in Counter(all_feedback).most_common(3)
    ]

    processing_time = round(time.time() - start_time, 2)

    return {
        "cluster_id": cluster_payload["cluster_id"],
        "cluster_size": len(results),
        "avg_score": round(avg_score, 2),
        "top_issues": top_issues,
        "processing_time": processing_time,
        "results": results
    }
