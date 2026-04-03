from pathlib import Path


def export_student_pdf(output_dir, student_feedback):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{student_feedback['student_id']}.pdf"

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        fallback_path = output_dir / f"{student_feedback['student_id']}.txt"
        with open(fallback_path, "w", encoding="utf-8") as file:
            file.write(student_feedback["email_text"])
        return str(fallback_path)

    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    y = height - 50

    lines = [
        f"Student ID: {student_feedback['student_id']}",
        f"Question: {student_feedback['question_id']}",
        f"Marks: {student_feedback['final_marks']}",
        "",
        "Tutoring Feedback:",
        student_feedback["tutoring_paragraph"],
        "",
        "Practice Question:",
        student_feedback["practice_question"],
    ]

    for line in lines:
        for wrapped_line in _wrap_text(str(line), 95):
            pdf.drawString(40, y, wrapped_line)
            y -= 16
            if y < 60:
                pdf.showPage()
                y = height - 50

    pdf.save()
    return str(output_path)


def _wrap_text(text, width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        proposal = f"{current} {word}"
        if len(proposal) <= width:
            current = proposal
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines
