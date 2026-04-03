
"""
HACKATHON-SAFE FAST OCR PIPELINE
Fast, stable, and much more practical than running TrOCR on every line.

Key changes:
- preload EasyOCR once
- no TrOCR by default
- Tesseract first
- EasyOCR only for low-confidence lines
- progress bar updates per page
- safer on Mac/MPS by forcing CPU for EasyOCR
"""

import json
import pandas as pd
from pathlib import Path
import os
import cv2
import numpy as np
import pytesseract
import zipfile
import argparse
import re
from PIL import Image
from io import BytesIO
from tqdm import tqdm
from collections import defaultdict
import warnings

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings(
    "ignore",
    message=".*pin_memory.*not supported on MPS.*"
)


import easyocr

CONF_THRESH = 55
TESS_PSMS = [6, 11]

reader = None


def get_reader():
    global reader
    if reader is None:
        print("Loading EasyOCR once...")
        reader = easyocr.Reader(["en"], gpu=False)
    return reader


def parse_filenames(names):
    patterns = [
        r"^(\w+)[_\-]sheet(\d+)\.(png|jpg|jpeg)$",
        r".*?[_\-\s]?(\w+)[_\-\s]p(\d+)\.(png|jpg|jpeg)$",
        r".*?[_\-\s](\w+)[_\-\s]page(\d+)\.(png|jpg|jpeg)$",
        r"^(\w+)[_\-](\d+)\.(png|jpg|jpeg)$",
        r".*?(\d+)pg(\d+)\.(png|jpg|jpeg)$",
        r"^(\d+)-(\d+)\.(png|jpg|jpeg)$",
    ]
    grouped = defaultdict(dict)

    for name in names:
        base = Path(name).name
        low = base.lower()
        if not low.endswith((".png", ".jpg", ".jpeg")):
            continue

        for pat in patterns:
            m = re.match(pat, base, re.IGNORECASE)
            if m:
                grouped[m.group(1)][int(m.group(2))] = name
                break

    return dict(grouped)


def clean_text(text):
    text = text.replace("\x0c", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[|\\/_]{2,}", " ", text)
    text = re.sub(r"([A-Za-z])\1{3,}", r"\1", text)
    return text.strip()


def preprocess_gray(pil_img):
    gray = np.array(pil_img.convert("L"))
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    return gray


def make_binary_variants(gray):
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    return [otsu, adaptive]


def segment_lines(bin_img):
    gray = bin_img.copy()

    if np.mean(gray) > 127:
        work = 255 - gray
    else:
        work = gray

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 3))
    dilated = cv2.dilate(work, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h, w = gray.shape[:2]
    boxes = []
    for c in contours:
        x, y, bw, bh = cv2.boundingRect(c)

        if bw < w * 0.15:
            continue
        if bh < 12:
            continue
        if bw * bh < 500:
            continue

        boxes.append((x, y, bw, bh))

    boxes.sort(key=lambda b: b[1])

    lines = []
    for x, y, bw, bh in boxes:
        pad = 6
        y1 = max(0, y - pad)
        y2 = min(h, y + bh + pad)
        x1 = max(0, x - pad)
        x2 = min(w, x + bw + pad)

        crop = gray[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        ch, cw = crop.shape[:2]
        if ch < 10 or cw < 20:
            continue

        lines.append(crop)

    if not lines:
        lines = [gray]

    return lines


def tesseract_ocr(img, psm):
    if img is None or img.size == 0:
        return {"text": "", "confidence": 0}

    h, w = img.shape[:2]
    if h < 10 or w < 20:
        return {"text": "", "confidence": 0}

    pil = Image.fromarray(img)

    try:
        data = pytesseract.image_to_data(
            pil,
            config=f"--oem 3 --psm {psm}",
            output_type=pytesseract.Output.DICT,
            timeout=8
        )
    except RuntimeError:
        return {"text": "", "confidence": 0}
    except Exception:
        return {"text": "", "confidence": 0}

    words, confs = [], []
    for w, c in zip(data["text"], data["conf"]):
        try:
            c = float(c)
        except:
            c = -1
        if w.strip() and c > 40:
            words.append(w)
            confs.append(c)

    text = clean_text(" ".join(words))
    conf = sum(confs) / len(confs) if confs else 0
    return {"text": text, "confidence": conf}


def best_tesseract(img):
    results = [tesseract_ocr(img, psm) for psm in TESS_PSMS]
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[0]


def easyocr_ocr(img):
    reader = get_reader()
    results = reader.readtext(img, detail=1, paragraph=False)

    words, confs = [], []
    for item in results:
        if len(item) == 3:
            _, text, conf = item
            if text.strip():
                words.append(text)
                confs.append(conf * 100)

    text = clean_text(" ".join(words))
    conf = sum(confs) / len(confs) if confs else 0
    return {"text": text, "confidence": conf}


def recognize_line(line_img):
    try:
        tess = best_tesseract(line_img)
    except Exception:
        tess = {"text": "", "confidence": 0}

    if tess["confidence"] >= 72 and len(tess["text"]) > 3:
        return tess

    try:
        easy = easyocr_ocr(line_img)
    except Exception:
        easy = {"text": "", "confidence": 0}

    if easy["confidence"] > tess["confidence"] + 4 and len(easy["text"]) >= max(3, len(tess["text"]) // 2):
        return easy

    return tess if tess["text"] else easy



def process_page(pil_img):
    gray = preprocess_gray(pil_img)
    variants = make_binary_variants(gray)

    best_page = {"text": "", "confidence": 0}

    for variant in variants:
        lines = segment_lines(variant)

        line_texts = []
        line_scores = []

        for line in lines:
            result = recognize_line(line)
            if result["text"]:
                line_texts.append(result["text"])
            if result["confidence"] > 0:
                line_scores.append(result["confidence"])

        page_text = clean_text(" ".join(line_texts))
        page_conf = sum(line_scores) / len(line_scores) if line_scores else 0

        if page_conf > best_page["confidence"]:
            best_page = {"text": page_text, "confidence": page_conf}

    return best_page


def run_pipeline(source):
    print("FAST HACKATHON OCR PIPELINE\n")

    get_reader()

    if os.path.isdir(source):
        all_names = [
            str(p) for p in Path(source).rglob("*")
            if p.suffix.lower() in {".png", ".jpg", ".jpeg"}
        ]
        read_file = lambda x: open(x, "rb").read()
    else:
        zf = zipfile.ZipFile(source)
        all_names = zf.namelist()
        read_file = lambda x: zf.read(x)

    grouped = parse_filenames(all_names)

    page_jobs = []
    for sid, pages in grouped.items():
        for page_num, page_path in sorted(pages.items()):
            page_jobs.append((sid, page_num, page_path))

    page_outputs = defaultdict(dict)

    for sid, page_num, page_path in tqdm(page_jobs, desc="OCR pages"):
        img = Image.open(BytesIO(read_file(page_path)))
        page_outputs[sid][page_num] = process_page(img)

    results = []
    flagged = 0

    for sid in sorted(page_outputs):
        ordered = page_outputs[sid]
        full_text = " ".join(ordered[p]["text"] for p in sorted(ordered))
        confs = [ordered[p]["confidence"] for p in sorted(ordered) if ordered[p]["confidence"] > 0]
        avg_conf = sum(confs) / len(confs) if confs else 0

        row = {
            "student_id": sid,
            "full_text": clean_text(full_text),
            "avg_confidence": round(avg_conf, 1),
            "flagged": avg_conf < CONF_THRESH
        }
        results.append(row)
        if row["flagged"]:
            flagged += 1

    avg = sum(r["avg_confidence"] for r in results) / len(results) if results else 0

    print("\n" + "-" * 40)
    print(f"Avg confidence: {round(avg, 1)}")
    print(f"Flagged: {flagged}")
    print("-" * 40)

    output_dir = Path("ocr_output")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    pd.DataFrame(results).to_csv(output_dir / "results.csv", index=False)

    print(f"Saved JSON: {output_dir / 'results.json'}")
    print(f"Saved CSV: {output_dir / 'results.csv'}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str, default=None)
    parser.add_argument("--zip", type=str, default=None)
    args = parser.parse_args()

    if args.folder:
        run_pipeline(args.folder)
    elif args.zip:
        run_pipeline(args.zip)
    else:
        print("Please provide --folder or --zip")
