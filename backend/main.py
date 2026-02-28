from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from dotenv import load_dotenv

# Import our custom engines
from ai_extractor import extract_plan_data 
from fhir_mapper import convert_to_fhir

# Load environment variables
load_dotenv()

# Initialize the Micro-service
app = FastAPI(
    title="Bima-FHIR NHCX Generator",
    description="Micro-service to convert unstructured insurance PDFs into NHCX-compliant FHIR bundles.",
    version="1.0.0"
)

# ---------------------------------------------------------
# CORS CONFIGURATION (Crucial for the Next.js Frontend)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your localhost:3000 frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up temporary storage for uploaded PDFs
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

@app.get("/")
def read_root():
    return {"status": "Bima-FHIR Micro-service is running and ready for NHCX conversion."}

@app.post("/api/v1/extract")
async def process_insurance_pdf(file: UploadFile = File(...)):
    """
    Core pipeline:
    1. Receives PDF
    2. Extracts structured data via Groq (Llama 3)
    3. Maps data to NHCX FHIR Bundle
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the uploaded file temporarily
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        print(f"--- Processing {file.filename} ---")
        
        # Step 1: Agentic AI Extraction (PDF -> Structured JSON)
        raw_data = await extract_plan_data(file_path)
        
        # Step 2: Configuration-Driven FHIR Mapping (JSON -> FHIR Bundle)
        fhir_bundle = convert_to_fhir(raw_data)
        
        print("--- Pipeline Complete ---")
        
        return {
            "message": "NHCX FHIR Bundle Generated Successfully",
            "filename": file.filename,
            "fhir_bundle": fhir_bundle # The final payload expected by the frontend
        }
        
    except Exception as e:
        print(f"Pipeline Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Always clean up the temporary PDF file to save server space
        if os.path.exists(file_path):
            os.remove(file_path)

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)