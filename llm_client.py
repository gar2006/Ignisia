import json
import os
import re
from dataclasses import dataclass


@dataclass
class LLMResponse:
    tutoring_paragraph: str
    practice_question: str
    email_text: str
    used_model: str
    generation_mode: str


def _safe_text(value):
    return (value or "").strip()


def _parse_marks_ratio(final_marks):
    text = _safe_text(final_marks)
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", text)
    if not match:
        return None, None
    scored = float(match.group(1))
    total = float(match.group(2))
    if total <= 0:
        return scored, None
    return scored, total


def _split_required_elements(required_elements):
    text = _safe_text(required_elements)
    if not text:
        return []
    parts = re.split(r"\||;|,|\n|•|- ", text)
    cleaned = []
    for part in parts:
        part = part.strip(" .:-")
        if len(part) >= 4:
            cleaned.append(part)
    deduped = []
    seen = set()
    for part in cleaned:
        key = part.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(part)
    return deduped[:6]


def _tokenize(text):
    return set(re.findall(r"[A-Za-z0-9]+", (text or "").lower()))


def _detect_present_and_missing(required_elements, student_answer):
    student_tokens = _tokenize(student_answer)
    present = []
    missing = []
    for element in required_elements:
        element_tokens = [
            token
            for token in re.findall(r"[A-Za-z0-9]+", element.lower())
            if len(token) > 2
        ]
        if not element_tokens:
            continue
        overlap = sum(1 for token in element_tokens if token in student_tokens)
        threshold = max(1, min(2, len(element_tokens)))
        if overlap >= threshold:
            present.append(element)
        else:
            missing.append(element)
    return present, missing


def _build_empathy_line(student_name, final_marks):
    scored, total = _parse_marks_ratio(final_marks)
    name = student_name or "Student"
    if scored is None or total is None:
        return (
            f"{name}, you have made a sincere attempt here, and this answer gives us "
            "a clear starting point for improvement."
        )

    ratio = scored / total if total else 0.0
    if ratio >= 0.8:
        return (
            f"{name}, you are very close to a strong answer and your core "
            "understanding is mostly in place."
        )
    if ratio >= 0.5:
        return (
            f"{name}, you understood an important part of the idea, but a few "
            "key steps or details reduced your marks."
        )
    return (
        f"{name}, there is effort in your response, but this concept needs a more "
        "structured revision so the main idea becomes secure."
    )


def _categorize_teacher_note(teacher_note, question_type):
    note = _safe_text(teacher_note).lower()
    if question_type == "math":
        if any(token in note for token in ["negative sign", "sign", "minus"]):
            return "sign_error"
        if any(token in note for token in ["step", "justify", "working"]):
            return "missing_steps"
        if any(token in note for token in ["formula", "substitute", "equation"]):
            return "formula_error"
        return "general_math"

    if question_type == "code":
        if any(token in note for token in ["syntax", "indent", "bracket", "parenthesis", "print"]):
            return "syntax_output"
        if any(token in note for token in ["condition", "logic", "branch", "if", "else", "modulo", "%"]):
            return "logic_error"
        if any(token in note for token in ["input", "output", "format", "display"]):
            return "io_error"
        return "general_code"

    if any(token in note for token in ["define", "definition", "meaning"]):
        return "definition_gap"
    if any(token in note for token in ["importance", "advantage", "use", "purpose"]):
        return "importance_gap"
    if any(token in note for token in ["example", "syntax", "declare", "declaration"]):
        return "syntax_example_gap"
    return "general_theory"


def _infer_question_type(question_text, model_answer):
    text = f"{question_text} {model_answer}".lower()
    code_signals = [
        "write a python program",
        "write a program",
        "write code",
        "python",
        "print(",
        "input(",
        "int(",
        "if ",
        "else",
        "while ",
        "for ",
        "num % 2",
    ]
    if any(token in text for token in code_signals):
        return "code"
    if any(
        token in text
        for token in ["solve", "equation", "simplify", "calculate", "find the value", "+", "-", "*", "/", "="]
    ):
        return "math"
    return "theory"


def _build_concept_recap(question_text, model_answer, required_elements, missing_elements):
    if missing_elements:
        focus_items = missing_elements[:3]
    elif required_elements:
        focus_items = required_elements[:3]
    else:
        focus_items = []

    if focus_items:
        return "To improve this answer, make sure you cover: " + "; ".join(focus_items) + "."

    clean_model = _safe_text(model_answer)
    recap = (
        "The expected answer should stay focused on the main concept in the question: "
        f"{_safe_text(question_text)}."
    )
    if clean_model:
        recap += f" A strong answer would include ideas such as {clean_model[:180]}."
    return recap


def _build_skill_focus_line(question_type, error_category):
    if question_type == "math":
        mapping = {
            "sign_error": "In algebraic working, a single missed sign can change the final answer completely, so each transformation must be checked carefully.",
            "missing_steps": "In mathematics, clear intermediate steps are important because they show both the method and the correctness of the final answer.",
            "formula_error": "When a formula or equation is used, each symbol and substitution has to match the required method exactly.",
            "general_math": "A strong maths answer needs both the correct method and a clearly justified final result.",
        }
        return mapping.get(error_category, mapping["general_math"])

    if question_type == "code":
        mapping = {
            "syntax_output": "In programming, even when the idea is correct, small syntax or output mistakes can stop the program from behaving as expected.",
            "logic_error": "For programming questions, the condition and decision-making logic have to match the problem exactly, not just approximately.",
            "io_error": "A complete program needs correct input handling as well as correct output for every case asked in the question.",
            "general_code": "A good code answer should include correct input, logic, and output in a complete flow.",
        }
        return mapping.get(error_category, mapping["general_code"])

    mapping = {
        "definition_gap": "For theory answers, the first step is to state the core definition clearly and accurately.",
        "importance_gap": "After the definition, you should explain why the concept matters and where it is useful.",
        "syntax_example_gap": "Theory answers become much stronger when they include the required syntax or an example in the correct form.",
        "general_theory": "A strong theory answer combines the definition, the explanation, and the required supporting detail.",
    }
    return mapping.get(error_category, mapping["general_theory"])


def _build_specific_mistake_line(teacher_note, present_elements, missing_elements):
    note = _safe_text(teacher_note)
    if note:
        base = f"The main issue your teacher identified was: {note}."
    else:
        base = (
            "The main issue was that some of the expected ideas were either incomplete "
            "or not explained clearly enough."
        )

    if missing_elements:
        return base + " The missing or weak parts were " + "; ".join(missing_elements[:3]) + "."
    if present_elements:
        return base + " You did show understanding of " + "; ".join(present_elements[:2]) + ", so that part can be built on."
    return base


def _build_next_steps(question_type, error_category, missing_elements):
    focus = missing_elements[:2]
    if question_type == "math":
        steps = {
            "sign_error": [
                "Rewrite each subtraction or negative term carefully before simplifying.",
                "Check the sign of each intermediate line before writing the final answer.",
            ],
            "missing_steps": [
                "Show one line at a time instead of jumping straight to the result.",
                "Add a short reason when you apply a formula or transform an expression.",
            ],
            "formula_error": [
                "Write the correct formula first before substituting values.",
                "Check each substituted value against the original question once more.",
            ],
            "general_math": [
                "Solve the problem one step at a time and verify the final answer against the question.",
                "Review where your working first starts to differ from the correct method.",
            ],
        }
    elif question_type == "code":
        steps = {
            "syntax_output": [
                "Trace the program line by line and check brackets, indentation, and print statements.",
                "Run through one sample input mentally and verify the exact output wording.",
            ],
            "logic_error": [
                "Test the condition separately with one even and one odd input.",
                "Check whether each branch matches the question before thinking about formatting.",
            ],
            "io_error": [
                "Confirm that the input is read in the correct type before using it.",
                "Make sure both required outputs are printed in the correct branch.",
            ],
            "general_code": [
                "Break the solution into input, condition, and output, then verify each part separately.",
                "Check the program with at least two sample cases before finalizing the answer.",
            ],
        }
    else:
        steps = {
            "definition_gap": [
                "Start your answer with one precise sentence defining the concept.",
                "Avoid vague wording and use the technical terms from the question.",
            ],
            "importance_gap": [
                "After the definition, add at least two clear uses or benefits.",
                "Link each importance point directly back to the concept named in the question.",
            ],
            "syntax_example_gap": [
                "Include the required syntax exactly in the standard format.",
                "Add one short valid example to show that you understand how it is used.",
            ],
            "general_theory": [
                "Structure the answer into definition, explanation, and example.",
                "Check that each part of the question has been answered explicitly.",
            ],
        }

    chosen_steps = steps.get(error_category, next(iter(steps.values())))
    if focus:
        chosen_steps = chosen_steps + [f"Pay extra attention to: {'; '.join(focus)}."]
    return "Next, focus on these improvements: " + " ".join(chosen_steps[:3])


def _build_practice_question(question_text, teacher_note, question_type, required_elements, missing_elements):
    focus = "; ".join((missing_elements or required_elements)[:3])
    note = _safe_text(teacher_note)
    if question_type == "code":
        return (
            "Practice question: Write a short program for a closely related case, then add 2-3 comments explaining each step. "
            + (f"Pay special attention to these ideas: {focus}. " if focus else "")
            + (f"While solving, make sure you avoid this mistake: {note}." if note else "")
        )
    if question_type == "math":
        return (
            "Practice question: Solve one similar problem step by step and write a brief reason beside each transformation. "
            + (f"Focus especially on {focus}. " if focus else "")
            + (f"Check carefully that you do not repeat this error: {note}." if note else "")
        )
    return (
        f'Practice question: Answer a similar question to "{_safe_text(question_text)}" in your own words. '
        + (f"Your answer should clearly include: {focus}. " if focus else "")
        + (f"Also make sure you avoid this issue: {note}." if note else "")
    )


def _build_email_text(student_name, final_marks, teacher_note, tutoring_paragraph, practice_question):
    note = _safe_text(teacher_note) or "Please review the key missing ideas listed below."
    return (
        f"Hi {student_name},\n\n"
        f"You were awarded {final_marks} for this question.\n"
        f"Teacher note: {note}\n\n"
        f"Feedback:\n{tutoring_paragraph}\n\n"
        f"{practice_question}\n"
    )


def _extract_json_payload(text):
    raw_text = _safe_text(text)
    if not raw_text:
        return None

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if fenced_match:
        try:
            return json.loads(fenced_match.group(1))
        except json.JSONDecodeError:
            pass

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw_text[start : end + 1])
        except json.JSONDecodeError:
            return None
    return None


def _fallback_response(
    student_name,
    question_text,
    model_answer,
    student_answer,
    teacher_note,
    final_marks,
    required_elements=None,
):
    required_list = _split_required_elements(required_elements)
    present_elements, missing_elements = _detect_present_and_missing(required_list, student_answer)
    question_type = _infer_question_type(question_text, model_answer)
    error_category = _categorize_teacher_note(teacher_note, question_type)
    empathy_line = _build_empathy_line(student_name, final_marks)
    mistake_line = _build_specific_mistake_line(teacher_note, present_elements, missing_elements)
    skill_focus_line = _build_skill_focus_line(question_type, error_category)
    concept_recap = _build_concept_recap(question_text, model_answer, required_list, missing_elements)
    next_steps = _build_next_steps(question_type, error_category, missing_elements)
    practice_question = _build_practice_question(
        question_text=question_text,
        teacher_note=teacher_note,
        question_type=question_type,
        required_elements=required_list,
        missing_elements=missing_elements,
    )
    answer_excerpt = _safe_text(student_answer)[:220]
    answer_line = ""
    if answer_excerpt:
        answer_line = f" In your submitted answer, you wrote: {answer_excerpt}."
    tutoring_paragraph = " ".join(
        [empathy_line, mistake_line, skill_focus_line, concept_recap, next_steps]
    ).strip() + answer_line
    email_text = _build_email_text(
        student_name=student_name,
        final_marks=final_marks,
        teacher_note=teacher_note,
        tutoring_paragraph=tutoring_paragraph,
        practice_question=practice_question,
    )
    return LLMResponse(
        tutoring_paragraph=tutoring_paragraph,
        practice_question=practice_question,
        email_text=email_text,
        used_model="local-rubric-generator",
        generation_mode="template",
    )


def generate_student_feedback(
    student_name,
    question_text,
    model_answer,
    student_answer,
    teacher_note,
    final_marks,
    required_elements=None,
):
    return _fallback_response(
        student_name=student_name,
        question_text=question_text,
        model_answer=model_answer,
        student_answer=student_answer,
        teacher_note=teacher_note,
        final_marks=final_marks,
        required_elements=required_elements,
    )
