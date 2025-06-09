# PDFSummarizer

A FastAPI-based service that uses Google's Gemini AI to summarize PDF documents and text. The service provides both synchronous and asynchronous processing capabilities, with Redis for job queue management.

## Prerequisites

- Docker installed

## Setup

1. Extract the zip file:
```bash
unzip BAPDFSummarizer.zip
cd BAPDFSummarizer
```

2. Start the application:
```bash
docker-compose up -d
```

The service will be available at:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Architecture

The service uses a two-container architecture:

1. **Application Container**
   - FastAPI application server
   - Worker process for job processing
   - Both components share the same codebase
   - Communicates with Redis for job queue management

2. **Redis Container**
   - Dedicated Redis server
   - Persistent storage for job queue
   - Data persistence enabled
   - Health checks implemented

## API Endpoints

### Version 1 (`/api/v1/`)

- `POST /summarize-text/` - Submit text for summarization
- `POST /summarize-pdf-async/` - Asynchronously process a PDF file
- `POST /summarize-pdf-sync/` - Synchronously process a PDF file
- `GET /job-status/{job_id}` - Check the status of a processing job
- `GET /list-text-jobs/` - List all text processing jobs

## Development

### Running Tests

Run tests using Docker:
```bash
docker-compose run app pytest tests/ -v
```

## Stopping the Service

To stop the service:
```bash
docker-compose down
```

## License

MIT 