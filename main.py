import os
import tempfile
import uvicorn
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from agent.workflow import run_extraction_workflow

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Quotation PDF Reader API",
    description="Extract structured JSON data from Quotation PDFs using LangGraph and Gemini 2.5 Flash",
    version="1.0.0"
)

# Setup a simple endpoint to verify the API is running
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/upload-quotation")
async def upload_quotation(file: UploadFile = File(...)):
    """
    Upload a quotation PDF and extract structured details.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    # Validate API Key exists
    if not os.getenv("GOOGLE_API_KEY"):
         raise HTTPException(status_code=500, detail="Server configuration error: GOOGLE_API_KEY is not set.")

    # Save uploaded file to a temporary location
    try:
        # Create a temporary file that will be cleaned up
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            # Read the whole file and write it to disk
            content = await file.read()
            tmp_file.write(content)
            tmp_pdf_path = tmp_file.name
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")

    # Run the workflow
    try:
        result = run_extraction_workflow(tmp_pdf_path)
        
        if not result["success"]:
            return JSONResponse(status_code=500, content={"error": result["error"]})
            
        return JSONResponse(status_code=200, content={"data": result["data"]})
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Workflow failed: {str(e)}"})
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_pdf_path):
            try:
                os.remove(tmp_pdf_path)
            except Exception:
                pass


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
