import tempfile
from pathlib import Path

import streamlit as st

from app_utils import (
    UPLOADS_DIR,
    prepare_source_from_upload,
    run_streamlit_pipeline,
    save_uploaded_file,
    slugify_name,
)


st.set_page_config(page_title="Ignisia Home", page_icon="📝", layout="wide")

st.title("Ignisia Grading Dashboard")
st.write("Upload student answer sheets and an answer-key CSV to run OCR, clustering, grading, and cost reporting.")

with st.sidebar:
    st.header("Run Setup")
    group_by = st.selectbox("Grouping mode", ["auto", "folder", "filename", "single"], index=0)

answer_key_file = st.file_uploader("Answer key CSV", type=["csv"])
manifest_file = st.file_uploader("Manifest (optional)", type=["json", "csv"])
sheet_input_file = st.file_uploader("Answer sheets input", type=["pdf", "png", "jpg", "jpeg", "zip"])

run_clicked = st.button("Run Pipeline", type="primary", use_container_width=True)

if run_clicked:
    if answer_key_file is None:
        st.error("Upload the answer-key CSV before running.")
    elif sheet_input_file is None:
        st.error("Upload a PDF, PNG/JPG image, or ZIP file of answer sheets.")
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            answer_key_path = temp_root / "Answer_Key_Q1_Q2.csv"
            save_uploaded_file(answer_key_file, answer_key_path)

            manifest_path = None
            if manifest_file is not None:
                manifest_path = temp_root / manifest_file.name
                save_uploaded_file(manifest_file, manifest_path)

            run_label = slugify_name(Path(sheet_input_file.name).stem)
            run_root = UPLOADS_DIR / run_label
            if run_root.exists():
                suffix_counter = 1
                while (UPLOADS_DIR / f"{run_label}_{suffix_counter}").exists():
                    suffix_counter += 1
                run_root = UPLOADS_DIR / f"{run_label}_{suffix_counter}"

            run_root.mkdir(parents=True, exist_ok=True)
            source_path = prepare_source_from_upload(sheet_input_file, run_root)

            results, summary, _, clustered_csv_path, results_json_path = run_streamlit_pipeline(
                source_path=source_path,
                answer_key_path=answer_key_path,
                group_by=group_by,
                manifest_path=manifest_path,
            )

            st.session_state["results"] = results
            st.session_state["summary"] = summary
            st.session_state["clustered_csv_path"] = str(clustered_csv_path)
            st.session_state["results_json_path"] = str(results_json_path)
            st.session_state["saved_dataset_path"] = str(run_root)

            st.success("Pipeline run completed.")
            st.info(f"Saved uploaded dataset at: {run_root}")
            st.page_link("pages/1_Dashboard.py", label="Open Dashboard", icon="📊")
            st.page_link("pages/2_Override_Review.py", label="Open Override Review", icon="🛠️")

if st.session_state.get("saved_dataset_path"):
    st.caption(f"Latest saved dataset: {st.session_state['saved_dataset_path']}")
