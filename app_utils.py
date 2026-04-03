import builtins
import copy
import json
import re
import sys
import zipfile
from contextlib import contextmanager
from pathlib import Path

import fitz
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
UPLOADS_DIR = ROOT_DIR / "uploads"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

from backend.cost_efficiency_logger import generate_cost_efficiency_summary
from backend.embedding import cluster_answers
from backend.run_pipeline import run_grading_pipeline
from ocr_final import run_pipeline as run_ocr_pipeline


@contextmanager
def non_interactive_review():
    original_input = builtins.input
    builtins.input = lambda prompt="": ""
    try:
        yield
    finally:
        builtins.input = original_input


def save_uploaded_file(uploaded_file, target_path):
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "wb") as file:
        file.write(uploaded_file.getbuffer())


def slugify_name(value):
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value).strip()).strip("_") or "run"


def prepare_source_from_upload(uploaded_file, run_root):
    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix == ".zip":
        source_path = run_root / uploaded_file.name
        save_uploaded_file(uploaded_file, source_path)
        extracted_dir = run_root / "extracted"
        extracted_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(source_path, "r") as archive:
            archive.extractall(extracted_dir)
        return source_path

    sheets_dir = run_root / "sheets"
    sheets_dir.mkdir(parents=True, exist_ok=True)

    if suffix in {".png", ".jpg", ".jpeg"}:
        save_uploaded_file(uploaded_file, sheets_dir / uploaded_file.name)
        return sheets_dir

    if suffix == ".pdf":
        pdf_bytes = uploaded_file.getbuffer()
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        base_name = Path(uploaded_file.name).stem

        for page_index, page in enumerate(pdf_doc, start=1):
            pix = page.get_pixmap()
            output_path = sheets_dir / f"{base_name}_page_{page_index}.png"
            pix.save(str(output_path))

        pdf_doc.close()
        return sheets_dir

    raise ValueError("Unsupported file type. Upload a PDF, PNG/JPG image, or ZIP file.")


def run_streamlit_pipeline(source_path, answer_key_path, group_by, manifest_path=None):
    stage_times = {}

    with st.status("Running OCR, clustering, and grading...", expanded=True) as status:
        status.write("Stage 1: OCR")
        with st.spinner("Running OCR..."):
            import time

            start = time.perf_counter()
            run_ocr_pipeline(
                str(source_path),
                group_by=group_by,
                manifest_path=str(manifest_path) if manifest_path else None,
            )
            stage_times["ocr_seconds"] = round(time.perf_counter() - start, 2)

        backend_ocr_results = BACKEND_DIR / "ocr_output" / "results.json"
        project_ocr_results = ROOT_DIR / "ocr_output" / "results.json"
        results_json_path = backend_ocr_results if backend_ocr_results.exists() else project_ocr_results

        clustered_csv_path = BACKEND_DIR / "final_clustered_grades.csv"
        clustered_json_path = BACKEND_DIR / "final_clustered_grades.json"

        status.write("Stage 2: Clustering")
        with st.spinner("Clustering answers..."):
            start = time.perf_counter()
            cluster_answers(
                results_json_path=results_json_path,
                output_csv_path=clustered_csv_path,
                output_json_path=clustered_json_path,
            )
            stage_times["clustering_seconds"] = round(time.perf_counter() - start, 2)

        output_path = BACKEND_DIR / "output.json"
        status.write("Stage 3: Grading")
        with st.spinner("Grading clusters..."):
            start = time.perf_counter()
            with non_interactive_review():
                results = run_grading_pipeline(
                    clustered_csv_path=clustered_csv_path,
                    answer_key_path=answer_key_path,
                    output_path=output_path,
                )
            stage_times["grading_seconds"] = round(time.perf_counter() - start, 2)

        stage_times["total_seconds"] = round(sum(stage_times.values()), 2)

        summary, _, _ = generate_cost_efficiency_summary(
            source=str(source_path),
            answer_key_path=answer_key_path,
            group_by=group_by,
            manifest_path=str(manifest_path) if manifest_path else None,
            model_name="gpt-4.1-mini-estimate",
            input_cost_per_1m=0.15,
            output_cost_per_1m=0.60,
            stage_times=stage_times,
            results_json_path=results_json_path,
            output_path=output_path,
        )
        status.update(label="Pipeline complete", state="complete", expanded=False)

    return results, summary, output_path, clustered_csv_path, results_json_path


def apply_cluster_override(results, question_id, cluster_id, marks_value, total_marks, reason_value):
    updated = copy.deepcopy(results)

    for cluster in updated.get(question_id, []):
        if cluster.get("cluster_id") != cluster_id:
            continue

        semantic = cluster.setdefault("semantic_evaluation", {})
        display_value = f"{marks_value}/{total_marks}"
        semantic["suggested_marks"] = marks_value
        semantic["suggested_marks_display"] = display_value
        semantic["reason"] = reason_value
        semantic["manual_reviewed"] = True

        for result in cluster.get("results", []):
            result["suggested_marks"] = display_value
            result["suggested_reason"] = reason_value

        break

    return updated


def build_cluster_overview_df(results):
    rows = []
    for question_id, clusters in results.items():
        for cluster in clusters:
            semantic = cluster.get("semantic_evaluation", {})
            suggested_marks = semantic.get("suggested_marks")
            rows.append({
                "question_id": question_id,
                "cluster_id": cluster.get("cluster_id"),
                "cluster_label": f"{question_id}-C{cluster.get('cluster_id')}",
                "cluster_size": cluster.get("cluster_size", 0),
                "avg_score": cluster.get("avg_score", 0),
                "confidence": semantic.get("confidence", 0),
                "suggested_marks": suggested_marks if suggested_marks is not None else 0,
                "total_marks": semantic.get("total_marks", 0),
                "threshold_passed": semantic.get("passed_similarity_threshold", False),
            })
    return pd.DataFrame(rows)


def get_cluster_by_label(results, cluster_label):
    for question_id, clusters in results.items():
        for cluster in clusters:
            label = f"{question_id}-C{cluster.get('cluster_id')}"
            if label == cluster_label:
                return question_id, cluster
    return None, None


def render_cost_summary(summary):
    st.subheader("Cost And Efficiency")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sheets", summary.get("sheet_count", 0))
    col2.metric("OCR (s)", summary["stage_times"].get("ocr_seconds", 0))
    col3.metric("Clustering (s)", summary["stage_times"].get("clustering_seconds", 0))
    col4.metric("Grading (s)", summary["stage_times"].get("grading_seconds", 0))

    batches = summary.get("batches", [])
    if batches:
        st.dataframe(pd.DataFrame(batches), use_container_width=True)
    st.caption(summary.get("token_estimation_note", ""))


def render_dashboard_graphs(results, summary):
    overview_df = build_cluster_overview_df(results)
    if overview_df.empty:
        st.info("No cluster data available yet.")
        return

    st.subheader("Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Questions", overview_df["question_id"].nunique())
    col2.metric("Total Clusters", len(overview_df))
    col3.metric("Total Answers", int(overview_df["cluster_size"].sum()))
    col4.metric("Avg Cluster Confidence", round(float(overview_df["confidence"].mean()), 2))

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("### Cluster Size Distribution")
        st.bar_chart(
            overview_df.set_index("cluster_label")["cluster_size"],
            use_container_width=True,
        )

    with right_col:
        st.markdown("### Suggested Marks By Cluster")
        st.bar_chart(
            overview_df.set_index("cluster_label")[["suggested_marks", "total_marks"]],
            use_container_width=True,
        )

    st.markdown("### Threshold Status")
    threshold_counts = (
        overview_df["threshold_passed"]
        .map({True: "Passed", False: "Manual Review"})
        .value_counts()
        .rename_axis("status")
        .reset_index(name="count")
    )
    if not threshold_counts.empty:
        st.bar_chart(threshold_counts.set_index("status")["count"], use_container_width=True)

    batches = summary.get("batches", [])
    if batches:
        batch_df = pd.DataFrame(batches)
        st.markdown("### Batch Processing Time")
        st.bar_chart(
            batch_df.set_index("batch_id")["estimated_processing_seconds"],
            use_container_width=True,
        )

    st.markdown("### Cluster Overview Table")
    st.dataframe(overview_df, use_container_width=True)


def build_outlier_df(results):
    rows = []
    for question_id, clusters in results.items():
        for cluster in clusters:
            semantic = cluster.get("semantic_evaluation", {})
            cluster_id = cluster.get("cluster_id")
            is_outlier = (
                cluster_id == -1
                or not semantic.get("passed_similarity_threshold", False)
                or semantic.get("confidence", 0) < 0.6
            )
            if not is_outlier:
                continue

            rows.append({
                "question_id": question_id,
                "cluster_id": cluster_id,
                "cluster_label": f"{question_id}-C{cluster_id}",
                "cluster_size": cluster.get("cluster_size", 0),
                "avg_score": cluster.get("avg_score", 0),
                "confidence": semantic.get("confidence", 0),
                "threshold_passed": semantic.get("passed_similarity_threshold", False),
                "suggested_marks_display": semantic.get("suggested_marks_display", "n/a"),
                "reason": semantic.get("reason", ""),
            })
    return pd.DataFrame(rows)


def render_outlier_graphs(results):
    outlier_df = build_outlier_df(results)
    if outlier_df.empty:
        st.success("No outlier clusters detected in the current run.")
        return

    st.subheader("Outlier Clusters")

    col1, col2, col3 = st.columns(3)
    col1.metric("Outlier Clusters", len(outlier_df))
    col2.metric("Outlier Answers", int(outlier_df["cluster_size"].sum()))
    col3.metric(
        "Avg Outlier Confidence",
        round(float(outlier_df["confidence"].mean()), 2),
    )

    st.markdown("### Outlier Cluster Sizes")
    st.bar_chart(
        outlier_df.set_index("cluster_label")["cluster_size"],
        use_container_width=True,
    )

    st.markdown("### Outlier Confidence")
    st.bar_chart(
        outlier_df.set_index("cluster_label")["confidence"],
        use_container_width=True,
    )

    st.markdown("### Outlier Summary")
    st.dataframe(
        outlier_df[
            [
                "question_id",
                "cluster_id",
                "cluster_size",
                "avg_score",
                "confidence",
                "threshold_passed",
                "suggested_marks_display",
                "reason",
            ]
        ],
        use_container_width=True,
    )


def render_downloads():
    results = st.session_state.get("results")
    summary = st.session_state.get("summary")
    clustered_csv_path = st.session_state.get("clustered_csv_path")

    if results is None:
        return

    st.subheader("Downloads")
    st.download_button(
        "Download reviewed_output.json",
        data=json.dumps(results, indent=2),
        file_name="reviewed_output.json",
        mime="application/json",
    )

    if summary is not None:
        st.download_button(
            "Download cost_efficiency_log.json",
            data=json.dumps(summary, indent=2),
            file_name="cost_efficiency_log.json",
            mime="application/json",
        )

    if clustered_csv_path and Path(clustered_csv_path).exists():
        with open(clustered_csv_path, "r", encoding="utf-8") as file:
            st.download_button(
                "Download final_clustered_grades.csv",
                data=file.read(),
                file_name="final_clustered_grades.csv",
                mime="text/csv",
            )


def load_cluster_answer_texts(clustered_csv_path, question_id, cluster_id):
    clustered_csv_path = Path(clustered_csv_path)
    if not clustered_csv_path.exists():
        return []

    df = pd.read_csv(clustered_csv_path)
    cluster_column = f"{question_id}_Cluster_ID"
    answer_column = f"{question_id}_Answer"

    if cluster_column not in df.columns or answer_column not in df.columns:
        return []

    filtered = df[df[cluster_column] == cluster_id]
    rows = []
    for _, row in filtered.iterrows():
        rows.append({
            "student_id": str(row.get("student_id", "")),
            "answer_text": str(row.get(answer_column, "")).strip(),
        })
    return rows


def load_cluster_image_paths(results_json_path, student_ids, saved_dataset_path=None):
    results_json_path = Path(results_json_path) if results_json_path else None
    saved_dataset_path = Path(saved_dataset_path) if saved_dataset_path else None

    if not results_json_path or not results_json_path.exists():
        return []

    with open(results_json_path, "r", encoding="utf-8") as file:
        ocr_rows = json.load(file)

    student_ids = {str(student_id) for student_id in student_ids}
    image_rows = []

    for row in ocr_rows:
        student_id = str(row.get("student_id", ""))
        if student_id not in student_ids:
            continue

        for source_file in row.get("source_files", []):
            source_path = Path(source_file)
            resolved_path = None

            if source_path.exists():
                resolved_path = source_path
            elif saved_dataset_path:
                candidate_paths = [
                    saved_dataset_path / source_path,
                    saved_dataset_path / "sheets" / source_path.name,
                    saved_dataset_path / source_path.name,
                ]
                for candidate in candidate_paths:
                    if candidate.exists():
                        resolved_path = candidate
                        break
                if resolved_path is None:
                    matches = list(saved_dataset_path.rglob(source_path.name))
                    if matches:
                        resolved_path = matches[0]
            if resolved_path is None:
                global_matches = list(UPLOADS_DIR.rglob(source_path.name))
                if global_matches:
                    resolved_path = global_matches[0]

            image_rows.append({
                "student_id": student_id,
                "image_path": str(resolved_path) if resolved_path else None,
                "source_file": str(source_file),
            })

    return image_rows
