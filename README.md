# PDFSummarizer

A FastAPI-based service that uses Google's Gemini AI to summarize PDF documents and text. The service provides both synchronous and asynchronous processing capabilities, with Redis for job queue management.

## Features

- PDF text extraction and summarization
- Text summarization
- Asynchronous processing with job status tracking
- Rate limiting handling with exponential backoff
- Redis-based job queue
- API versioning (v1)
- Docker-based deployment
- Comprehensive test suite

## API Endpoints

### Version 1 (`/api/v1/`)

- `POST /summarize-text/` - Submit text for summarization
- `POST /summarize-pdf-async/` - Asynchronously process a PDF file
- `POST /summarize-pdf-sync/` - Synchronously process a PDF file
- `GET /job-status/{job_id}` - Check the status of a processing job
- `GET /list-text-jobs/` - List all text processing jobs

## Setup

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone the repository:
```bash
git clone <repository-url>
cd pdfsummarizer
```

3. Start all services (API, Worker, and Redis) with a single command:
```bash
docker-compose up -d
```

The service will be available at:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Architecture

The service uses a microservices architecture with three main components:
1. API Server (FastAPI) - Handles HTTP requests and queues jobs
2. Worker - Processes jobs from the queue using Gemini AI
3. Redis - Manages job queue and stores results

All services are containerized and can be managed through Docker Compose.

## Error Handling

- Rate limiting is handled with exponential backoff
- Failed jobs are retried up to 3 times
- Detailed error messages are provided in the API responses

## Development

### Running Tests

The project includes both unit and integration tests. To run the tests:

1. Run all tests:
```bash
docker-compose run api pytest tests/ -v
```

2. Run specific test categories:
```bash
# Run only unit tests
docker-compose run api pytest tests/unit/ -v

# Run only integration tests
docker-compose run api pytest tests/integration/ -v
```

3. Run specific test files:
```bash
docker-compose run api pytest tests/unit/test_pdf_extraction.py -v
```

4. Run with additional options:
```bash
# Show print statements
docker-compose run api pytest -s

# Show more detailed output
docker-compose run api pytest -vv
```

### Test Structure

- `tests/unit/` - Unit tests for individual components
  - `test_pdf_extraction.py` - Tests for PDF text extraction
  - `test_markdown_conversion.py` - Tests for markdown conversion

- `tests/integration/` - Integration tests for API endpoints
  - `test_api_endpoints.py` - Tests for all API endpoints

### Adding New Tests

1. Create test files in the appropriate directory (`unit/` or `integration/`)
2. Follow the existing test patterns
3. Run tests to ensure they pass
4. Update this documentation if adding new test categories

## Stopping the Services

To stop all services:
```bash
docker-compose down
```

## License

MIT 