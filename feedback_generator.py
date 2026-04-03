import json
from pathlib import Path

from cluster_processor import group_by_cluster
from csv_loader import load_csv, load_teacher_answers
from email_exporter import export_email_text
from llm_client import generate_student_feedback
from pdf_exporter import export_student_pdf
from review_store import (
    build_review_lookup,
    build_reviews_from_grading_output,
    load_cluster_reviews,
)


def generate_feedback_packages(
    review_path,
    clustered_csv_path,
    answer_key_path,
    grading_output_path,
    output_dir=None,
):
    backend_dir = Path(__file__).resolve().parent
    output_dir = Path(output_dir or backend_dir / 'exports')
    pdf_dir = output_dir / 'pdfs'
    email_dir = output_dir / 'emails'
    json_output_path = output_dir / 'student_feedback.json'
    generated_review_path = output_dir / 'cluster_reviews.generated.json'
    output_dir.mkdir(parents=True, exist_ok=True)

    if review_path:
        reviews = load_cluster_reviews(review_path)
    else:
        reviews = build_reviews_from_grading_output(
            grading_output_path=grading_output_path,
            generated_review_path=generated_review_path,
        )
    review_lookup = build_review_lookup(reviews)
    clustered_answers = group_by_cluster(load_csv(clustered_csv_path))
    teacher_answers = load_teacher_answers(answer_key_path)

    with open(grading_output_path, 'r', encoding='utf-8') as file:
        grading_output = json.load(file)

    feedback_rows = []
    for question_id, clusters in grading_output.items():
        print(f"Generating feedback for {question_id}...")
        for cluster in clusters:
            cluster_key = (question_id, int(cluster['cluster_id']))
            review = review_lookup.get(cluster_key)
            if not review:
                continue

            teacher_data = teacher_answers.get(question_id, {})
            student_answers = clustered_answers.get(cluster_key, [])
            answer_lookup = {
                answer['student_id']: answer['raw_text']
                for answer in student_answers
            }

            for student in cluster.get('results', []):
                student_id = student['student_id']
                print(
                    f"  Processing cluster {cluster['cluster_id']} "
                    f"student {student_id}..."
                )
                student_answer = answer_lookup.get(student_id, '')
                llm_result = generate_student_feedback(
                    student_name=f'Student {student_id}',
                    question_text=teacher_data.get('question', ''),
                    model_answer=teacher_data.get('model_answer', ''),
                    student_answer=student_answer,
                    teacher_note=review['teacher_note'],
                    final_marks=review['final_marks'],
                    required_elements=teacher_data.get('required', ''),
                )
                feedback_record = {
                    'student_id': student_id,
                    'question_id': question_id,
                    'cluster_id': cluster['cluster_id'],
                    'final_marks': review['final_marks'],
                    'teacher_note': review['teacher_note'],
                    'student_answer': student_answer,
                    'tutoring_paragraph': llm_result.tutoring_paragraph,
                    'practice_question': llm_result.practice_question,
                    'email_text': llm_result.email_text,
                    'generation_mode': llm_result.generation_mode,
                    'used_model': llm_result.used_model,
                }
                feedback_record['pdf_path'] = export_student_pdf(pdf_dir, feedback_record)
                feedback_record['email_path'] = export_email_text(email_dir, feedback_record)
                feedback_rows.append(feedback_record)

    with open(json_output_path, 'w', encoding='utf-8') as file:
        json.dump(feedback_rows, file, indent=2)

    return {
        'feedback_path': str(json_output_path),
        'pdf_dir': str(pdf_dir),
        'email_dir': str(email_dir),
        'review_path': str(generated_review_path if not review_path else Path(review_path)),
        'student_feedback': feedback_rows,
    }
