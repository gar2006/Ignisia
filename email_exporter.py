from pathlib import Path


def export_email_text(output_dir, student_feedback):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{student_feedback['student_id']}.txt"
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(student_feedback["email_text"])
    return str(output_path)
