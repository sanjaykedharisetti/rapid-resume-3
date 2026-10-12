# Matchly AI — Resume & Job Description Matching System

An end-to-end, production-grade AI-powered web application that analyzes and matches resumes with job descriptions using Natural Language Processing (NLP). The system parses PDF and DOCX resumes, extracts key skills and qualifications, computes hybrid semantic similarity and keyword overlap scores, and generates actionable recommendations with visual interactive analytics.

---

## 🌟 Key Features

1. **Multi-Format Resume Ingestion**:
   - High-fidelity PDF parsing via **PyMuPDF (`fitz`)**
   - Word document parsing via **python-docx**
   - Strict validation with file-size and file-type enforcement

2. **Advanced NLP Matching Pipeline**:
   - **Semantic Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`) generating 384-dimensional dense vectors with cosine similarity
   - **Lexical Overlap**: TF-IDF vectorization with n-gram analysis and keyword extraction
   - **Entity & Skill Extraction**: Custom rule-based dictionary matcher covering 1,000+ technical, soft, and domain-specific skills, plus educational qualification detectors
   - **Weighted Scoring Algorithm**: Configurable breakdown across Semantic Similarity (40%), Technical Skills (35%), Qualifications & Experience (15%), and Keyword Overlap (10%)

3. **AI Resume Optimizer & ATS Score Improvement (New)**:
   - **Truthful Optimization Engine**: Reorganizes resume sections, elevates matching skills, normalizes technical aliases, and infuses high-impact action verbs without hallucinating unearned skills or qualifications.
   - **Iterative Refinement Loop**: Tests multiple structural permutations against target job description (targeting 85%+ compatibility) and recalculates scores with the exact same scoring algorithm.
   - **Side-by-Side Comparison**: Live visual diff comparing original vs. ATS-tailored content with transparency change log and candidate prompts.
   - **Multi-Format Document Export**: Generates clean single-column ATS Resume PDFs (ReportLab), comprehensive ATS Score Reports, and editable Microsoft Word documents (`.docx`).

4. **Rich Insights & Feedback**:
   - Matching score with animated circular progress indicator and radar charts
   - Matched vs. Missing skill breakdown with contextual keyword highlighting
   - Concrete resume optimization suggestions and algorithmic limitations disclaimer
   - PDF analysis report export using **ReportLab**

5. **Modern Responsive UI**:
   - Built with **React 18**, **Vite**, and **Tailwind CSS**
   - Sleek glassmorphism aesthetic with responsive layouts and dark-mode accents
   - Interactive charts via **Recharts** (Category breakdown, Skill match bars, Compatibility radar)
   - Analysis history browser with SQLite persistence and instant deletion

---

## 🏗️ Architecture & Project Structure

```text
rapid-resume-3/
├── backend/
│   ├── app/
│   │   ├── api/             # API routes (match, history, health, report)
│   │   ├── core/            # Config, settings, and logging
│   │   ├── models/          # SQLAlchemy async ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Parsers, NLP matcher, PDF generator
│   │   ├── database.py      # Async SQLite / PostgreSQL session setup
│   │   └── main.py          # FastAPI application factory & middleware
│   ├── tests/               # Pytest suite with unit and e2e tests
│   ├── Dockerfile           # Production container definition
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Navbar, Footer, DropZone, ScoreCircle, Charts
│   │   ├── pages/           # HomePage, MatcherPage, ResultsPage, HistoryPage
│   │   ├── services/        # Axios API client
│   │   ├── utils/           # Formatting and color helpers
│   │   ├── App.jsx          # Route configuration
│   │   └── index.css        # Tailwind styles and custom utilities
│   ├── Dockerfile           # Multi-stage production container
│   ├── Dockerfile.dev       # Development container
│   └── package.json         # NPM dependencies and scripts
└── docker-compose.yml       # Multi-container orchestration
```

---

## 🚀 Quick Start Guide

### ⚡ One-Click Start (Recommended)
You can launch everything (backend, frontend, and browser) with a single command or double click:

- **Windows Batch (Command Prompt or Explorer)**:
  Double-click [**`start.bat`**](file:///c:/Users/sanja/OneDrive/Desktop/rapid-resume-3/start.bat) or run:
  ```cmd
  .\start.bat
  ```

- **PowerShell**:
  ```powershell
  .\start.ps1
  ```

*This automatically configures virtual environments, installs missing dependencies, boots up FastAPI & Vite, and opens your browser directly to `http://localhost:5173`.*

---

### Manual Setup

#### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> **Backend API Docs**: Once started, open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

#### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

> **Frontend Application**: Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### Option 2: Running with Docker Compose

To launch both backend and frontend in isolated containers:

```bash
# From the project root
docker compose up --build
```

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend: [http://localhost:8000](http://localhost:8000)
- Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Healthcheck and runtime environment details |
| `POST` | `/api/match` | Upload resume (`.pdf`/`.docx`) + Job Description string to calculate score |
| `GET` | `/api/history` | Retrieve past analysis sessions |
| `GET` | `/api/history/{id}` | Retrieve specific analysis details |
| `DELETE` | `/api/history/{id}` | Delete an analysis record |
| `GET` | `/api/report/{id}/download` | Download synthesized PDF report |

---

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

Unit tests execute without downloading external model weights via mocked transformers. End-to-end tests validate end-to-end parsing, embedding, and scoring workflows.

---

## 🛡️ License & Acknowledgments
Built with FastAPI, PyMuPDF, Sentence-Transformers, spaCy, scikit-learn, React, Vite, and Tailwind CSS.
