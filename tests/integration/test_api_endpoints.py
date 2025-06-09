import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "PDFSummarizer API"

def test_summarize_text_endpoint():
    test_text = "This is a test text for summarization."
    response = client.post(
        "/api/v1/summarize-text/",
        json={"text": test_text}
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "message" in data

def test_job_status_endpoint():
    # First create a job
    test_text = "This is a test text for summarization."
    response = client.post(
        "/api/v1/summarize-text/",
        json={"text": test_text}
    )
    job_id = response.json()["job_id"]
    
    # Then check its status
    response = client.get(f"/api/v1/job-status/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_invalid_text_input():
    response = client.post(
        "/api/v1/summarize-text/",
        json={"invalid_field": "test"}
    )
    assert response.status_code == 422  # Validation error

def test_list_text_jobs():
    response = client.get("/api/v1/list-text-jobs/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "jobs" in data
    assert isinstance(data["jobs"], list) 