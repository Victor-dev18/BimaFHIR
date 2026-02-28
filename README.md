# BimaFHIR ⚡️
**Automated PDF to NHCX-aligned Insurance Plan FHIR Bundle**

**Hackathon Problem Statement 03:** Publishing NHCX-compliant insurance plans is manual & complex. 
**Our Solution:** BimaFHIR is an intelligent, edge-ready microservice that converts unstructured insurance policy PDFs into strictly validated, NHCX-compliant FHIR R4 Bundles in under 5 seconds, featuring a complete Human-in-the-Loop (HITL) validation dashboard.

## 🚀 Key Features
* **Vision-Based Table Extraction:** Utilizes LlamaParse to accurately extract complex tabular data (Sub-limits, Co-pays, ICD Exclusions) without scrambling rows.
* **Agentic LPU Processing:** Powered by Groq (Llama-3.3-70B) for lightning-fast, highly accurate data mapping forced into strict Pydantic JSON schemas.
* **Strict NRCeS Compliance:** Uses the `fhir.resources` Python library to guarantee the output is a valid `Collection` Bundle with correct NDHM CodeSystems.
* **Human-in-the-Loop (HITL) UI:** A Next.js split-pane dashboard allowing underwriters to visually verify the PDF against the generated FHIR JSON, edit values in real-time, and catch schema errors before final download.

## 🏗️ System Architecture
1. **Frontend:** Next.js (React), Tailwind CSS, Lucide Icons.
2. **Microservice Backend:** FastAPI (Python).
3. **AI Pipeline:** LlamaParse (PDF-to-Markdown) -> Groq API (Structured JSON Extraction).

## 💻 Local Setup Instructions

### 1. Backend Setup
\`\`\`bash
cd backend
python -m venv venv
# Activate venv (Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
\`\`\`
*Create a `.env` file in the `backend` directory with `GROQ_API_KEY` and `LLAMA_CLOUD_API_KEY`.*
Run the server: `uvicorn main:app --reload`

### 2. Frontend Setup
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`
*Navigate to `http://localhost:3000` to access the HITL Dashboard.*
