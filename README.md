# IGNISIA'26 | Team Hexora
## ED01: AI-Assisted Answer Clustering & Grading Acceleration Engine

An AI-assisted grading system that helps faculty evaluate subjective exam answers faster by clustering semantically similar responses, highlighting rubric matches, and isolating edge cases such as partially correct answers.

## Problem Statement

Faculty spend hours grading subjective answers, often reviewing the same responses repeatedly. This causes:

- Time-consuming evaluation
- Fatigue and reduced grading accuracy
- Inconsistent marking across similar answers

Traditional systems treat each answer independently and fail to:

- Group similar answers together
- Understand semantic similarity
- Handle multilingual responses such as English, Hindi, and Hinglish

## Objective

Build a system that organizes answer sheets by meaning so that a professor can:

- grade one representative answer
- apply the same score to similar responses
- review unique or uncertain answers separately

This improves grading speed, consistency, and efficiency.

## Proposed Solution

The system digitizes handwritten answer sheets through an OCR pipeline, converts answers into multilingual semantic embeddings, and clusters them by meaning using unsupervised learning.

This enables:

- cluster-based grading
- one-click grading for similar answers
- multilingual grouping across English, Hindi, and Hinglish
- smart detection of formula-correct but calculation-wrong responses
- review of outliers and uncertain clusters

Our architecture aims to reduce grading workload by up to 80%.

## Technical Approach

### 1. OCR Pipeline
Convert handwritten answer sheets into digital text.

### 2. Semantic Embeddings
Transform answers into semantic vectors using multilingual embedding models.

### 3. Clustering Engine
Group similar answers using clustering methods such as:

- HDBSCAN
- DBSCAN
- K-Means

### 4. Edge Case Detection
Detect partial-credit cases such as:

- correct concept but wrong calculation
- incomplete explanation
- unusual or outlier answers

### 5. Dashboard Interface
Provide a dashboard for:

- viewing answer clusters
- grading representative answers
- applying scores in bulk
- reviewing outliers and confidence levels

## Tech Stack

### OCR and Computer Vision
- OpenCV
- Tesseract
- EasyOCR

### NLP and Embeddings
- Sentence-Transformers
- MiniLM
- LaBSE

### Clustering and Visualization
- Scikit-learn
- HDBSCAN
- UMAP

### Backend and Logic
- Python
- FastAPI
- Regex
- SymPy

### Frontend Dashboard
- Streamlit

### Deployment
- Streamlit Cloud

## Unique Features

- **Cluster-Based Grading**  
  Grade once and apply the same score to all similar answers.

- **Cross-Lingual Clustering**  
  Group English, Hindi, and Hinglish answers into the same semantic cluster.

- **Smart Error Detection**  
  Detect answers where the formula is correct but the calculation is wrong.

- **Confidence and Outlier Detection**  
  Flag uncertain clusters and unique responses for manual review.

- **Time-Saved Analytics**  
  Show grading reduction, for example: 100 answers reduced to 14 grading actions.

- **Explainable AI Feedback**  
  Show why an answer was assigned a particular grade.

- **Auto Feedback Generation**  
  Generate personalized feedback for students cluster-wise.

- **Class Performance Dashboard**  
  Visualize strong topics, weak concepts, and common mistakes.

## Feasibility

This project is feasible because:

- it uses existing OCR, NLP, and clustering technologies
- handwritten datasets and exam-style answer sets can be collected or generated
- the system is modular and each component can be developed independently
- it can scale from small batches to large classroom workloads
- it is computationally practical on standard GPUs or cloud platforms

## Impact and Benefits

- **Faster Grading**  
  Reduces evaluation time significantly.

- **Consistency**  
  Ensures similar answers receive uniform marks.

- **Reduced Faculty Fatigue**  
  Minimizes repetitive grading work.

- **Better Insights**  
  Helps identify common misconceptions and performance trends.

- **Multilingual Support**  
  Handles English and Hindi mixed responses.

- **Scalability**  
  Efficiently processes large batches of answer sheets.

## Expected Outcome

A grader dashboard where a professor can upload scanned answer sheets and immediately see:

- semantically grouped answer clusters
- rubric keyword highlights
- partial-credit edge cases
- outlier answers needing manual review
- analytics on time saved and grading efficiency

## Future Scope

- stronger handwritten OCR with specialized models
- better multilingual support across more regional languages
- automated rubric learning
- LMS/institution integration
- student feedback reports and performance summaries

## Team

**Team Hexora**  
IGNISIA'26

## Thank You
