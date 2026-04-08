# AI Resume Analyzer + Interview Cracker System

LSTM/GRU-powered platform for resume analysis, interview preparation, and career optimization.

---

## Overview

This project simulates a complete hiring pipeline using artificial intelligence. It evaluates resumes using deep learning, compares them with job descriptions, predicts selection probability, and prepares candidates through AI-driven interview simulations.

It is designed as a combination of a final-year academic project and a production-level startup concept.

---

## Key Capabilities

* Resume parsing (PDF/DOCX)
* Deep learning-based ATS scoring (LSTM/GRU)
* Semantic resume–job matching
* Skill gap detection and recommendations
* AI-generated interview questions (HR, Technical, Behavioral)
* Answer evaluation with scoring and feedback
* Resume rewriting for impact improvement
* Candidate ranking simulation
* Skill roadmap generation
* Project recommendation engine
* Progress tracking dashboard

---

## System Architecture

```
Frontend (React + Tailwind)
        ↓
API Layer (FastAPI)
        ↓
AI Engine
   ├── LSTM/GRU Model (Resume-JD Matching)
   ├── NLP Engine (spaCy + TF-IDF)
   ├── Interview Generator
   ├── Answer Evaluator
   └── Recommendation System
        ↓
Storage (JSON / Filesystem)
```

---

## Machine Learning Design

### Resume Matching Model

* Architecture: Dual-input Bi-LSTM / GRU
* Inputs:

  * Resume text
  * Job description
* Outputs:

  * ATS Score (0–100)
  * Selection probability

### Processing Pipeline

1. Text extraction
2. Cleaning and normalization
3. Tokenization
4. Sequence padding
5. Embedding layer
6. LSTM/GRU encoding
7. Dense layers for prediction

Fallback mechanism uses TF-IDF cosine similarity when model is not trained.

---

## Features Breakdown

### Resume Analysis

* Extracts and processes resume content
* Identifies matching and missing skills
* Generates ATS score

### Interview Simulator

* Generates role-specific questions
* Categories: HR, Technical, Behavioral
* Difficulty levels supported

### Answer Evaluation

* Scores responses (0–10)
* Provides structured feedback
* Suggests improved answers

### Skill Gap Intelligence

* Detects missing competencies
* Generates structured learning roadmap

### Resume Enhancement

* Converts weak statements into strong, measurable bullet points

### Candidate Ranking

* Simulates comparison with multiple candidates
* Provides percentile ranking

### Project Suggestions

* Recommends portfolio projects based on missing skills

### Progress Tracking

* Tracks ATS score improvement over time

---

## Technology Stack

### Frontend

* React (Vite)
* Tailwind CSS
* Recharts

### Backend

* FastAPI
* Uvicorn

### AI / Machine Learning

* TensorFlow / Keras (LSTM, GRU)
* scikit-learn
* spaCy

### Utilities

* PyPDF2
* python-docx
* Web Speech API

---

## Folder Structure

```
project/
├── backend/
│   ├── main.py
│   ├── train_model.py
│   ├── requirements.txt
│   └── utils/
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── tailwind.config.js
│
└── README.md
```

---

## Installation Guide

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## API Overview

| Endpoint            | Description         |
| ------------------- | ------------------- |
| /upload-resume      | Upload resume       |
| /analyze-resume     | ATS scoring         |
| /generate-questions | Interview questions |
| /evaluate-answer    | Answer scoring      |
| /skill-roadmap      | Learning roadmap    |
| /suggest-projects   | Project suggestions |
| /candidate-ranking  | Ranking simulation  |
| /rewrite-resume     | Resume enhancement  |
| /weakness-analysis  | Resume evaluation   |

---

## Deployment

### Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
npm run build
```

Deploy frontend on Vercel or Netlify and backend on any cloud VM or container service.

---

## Use Cases

* Students preparing for placements
* Job seekers optimizing resumes
* Career coaching platforms
* Interview preparation tools

---

## Future Enhancements

* Transformer-based semantic matching (BERT)
* Real-time interview feedback with audio analysis
* LinkedIn and GitHub profile integration
* Multi-language resume support

---

## Contribution

Contributions are welcome. Fork the repository and submit a pull request.

---

## License

This project is intended for educational and demonstration purposes.
