from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import tempfile
import redis
import json
from services.markdown_service import extract_text_from_pdf, convert_to_markdown
from services.gemini_service import setup_gemini, generate_markdown_and_summary
from services.redis_service import (
    add_to_queue, 
    get_job_status, 
    PDF_PROCESSING_STREAM, 
    GEMINI_PROCESSING_STREAM
)
import time
from config import GEMINI_API_KEY

# API version
API_V1_STR = "/api/v1"

app = FastAPI(
    title="PDFSummarizer API",
    description="API for summarizing PDF documents and text using Google's Gemini AI",
    version="1.0.0",
    openapi_url=f"{API_V1_STR}/openapi.json"
)

# Redis connection
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'redis'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=0
)

# Stream name
TEXT_PROCESSING_STREAM = 'text_processing'

# Setup Gemini API
if GEMINI_API_KEY:
    setup_gemini(GEMINI_API_KEY)
    print("✓ Gemini API setup completed successfully")
else:
    print("⚠ Warning: GEMINI_API_KEY not set in config.py. Text summarization will not work.")

class TextInput(BaseModel):
    text: str

@app.get("/")
def root():
    return {
        "message": "PDFSummarizer API",
        "version": "1.0.0",
        "docs_url": f"{API_V1_STR}/docs",
        "redoc_url": f"{API_V1_STR}/redoc"
    }

@app.post(f"{API_V1_STR}/summarize-text/")
async def process_text(text_input: TextInput):
    """Endpoint that accepts text and publishes it to Redis stream."""
    try:
        # Add message to Redis stream
        message_id = redis_client.xadd(
            TEXT_PROCESSING_STREAM,
            {'text': json.dumps(text_input.text)}
        )
        
        return {
            "message": "Text processing job queued",
            "job_id": message_id.decode('utf-8')
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {str(e)}"}
        )

@app.post(f"{API_V1_STR}/summarize-pdf-async/")
async def summarize_pdf_async(file: UploadFile = File(...)):
    """Asynchronous endpoint that queues a PDF for summarization."""
    # Check if the uploaded file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(
            status_code=400,
            content={"message": "Only PDF files are allowed"}
        )
    
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Extract text from the PDF using PyPDF
            text = extract_text_from_pdf(temp_path)
            
            # Add the text to the Redis stream for worker processing
            message_id = redis_client.xadd(
                TEXT_PROCESSING_STREAM,
                {'text': json.dumps(text)}
            )
            
            return {
                "message": "PDF processing job queued",
                "job_id": message_id.decode('utf-8'),
                "status": "queued"
            }
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {str(e)}"}
        )

@app.post(f"{API_V1_STR}/summarize-pdf-sync/")
async def summarize_pdf_sync(file: UploadFile = File(...)):
    """Synchronous endpoint that processes the PDF immediately with Gemini."""
    if not GEMINI_API_KEY:
        return JSONResponse(
            status_code=500,
            content={"message": "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."}
        )
        
    # Check if the uploaded file is a PDF
    if not file.filename.endswith('.pdf'):
        return JSONResponse(
            status_code=400,
            content={"message": "Only PDF files are allowed"}
        )
    
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Extract text from the PDF
            text = extract_text_from_pdf(temp_path)
            
            # Generate markdown and summary using Gemini
            markdown_sections, summary = generate_markdown_and_summary(text)
            
            return {
                "message": "PDF processed successfully",
                "filename": file.filename,
                "summary": summary,
                "markdown_sections": markdown_sections
            }
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {str(e)}"}
        )

@app.get(f"{API_V1_STR}/job-status/{{job_id}}")
async def check_job_status(job_id: str):
    """Check the status of a processing job."""
    status = get_job_status(job_id)
    return status

@app.get(f"{API_V1_STR}/list-text-jobs/")
async def list_text_jobs():
    """List all text inputs submitted to /summarize-text/ with their summaries."""
    try:
        # Get all messages from the stream
        messages = redis_client.xrange(TEXT_PROCESSING_STREAM, min='-', max='+')
        text_inputs = []
        for msg_id, msg_data in messages:
            msg_id_str = msg_id.decode('utf-8')
            try:
                # Get summary from Redis if available
                summary_data = redis_client.hgetall(f"text_summary:{msg_id_str}")
                if summary_data:
                    summary = summary_data.get(b'summary', b'').decode('utf-8')
                    status = summary_data.get(b'status', b'processing').decode('utf-8')
                else:
                    summary = None
                    status = 'queued'
                
                text_inputs.append({
                    "job_id": msg_id_str,
                    "summary": summary,
                    "status": status
                })
            except Exception as e:
                text_inputs.append({
                    "job_id": msg_id_str,
                    "summary": None,
                    "status": "error",
                    "error": str(e)
                })
        return {"jobs": text_inputs}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {str(e)}"}
        ) 