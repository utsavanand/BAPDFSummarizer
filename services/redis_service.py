import redis
import json
import os
from typing import Dict, Any

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0
)

# Stream names
TEXT_PROCESSING_STREAM = 'text_processing'
PDF_PROCESSING_STREAM = 'pdf_processing'
GEMINI_PROCESSING_STREAM = 'gemini_processing'

def add_to_queue(stream_name: str, job_data: Dict[str, Any]) -> str:
    """
    Add a job to the specified Redis stream.
    
    Args:
        stream_name: Name of the Redis stream
        job_data: Dictionary containing job data
        
    Returns:
        str: Job ID
    """
    # Add initial status
    job_data['status'] = 'queued'
    job_data['progress'] = 0
    
    # Add to stream
    job_id = redis_client.xadd(stream_name, job_data)
    
    return job_id

def get_job_status(job_id: str) -> dict:
    """
    Get the status of a job from Redis.
    Returns a dict with 'original' (first message) and 'latest' (last message) for the job, or {'status': 'not_found'} if not found.
    """
    for stream in [PDF_PROCESSING_STREAM, GEMINI_PROCESSING_STREAM]:
        messages = redis_client.xrange(stream, min=job_id, max='+')
        if messages:
            # Return both first and last message
            return {
                'original': messages[0][1],
                'latest': messages[-1][1]
            }
    return {'status': 'not_found'}

def update_job_status(job_id: str, status: str, progress: int = None, result: dict = None) -> None:
    """
    Update the status of a job in Redis.
    Only updates the stream where the job was originally created.
    """
    # Find which stream contains the job
    target_stream = None
    for stream in [PDF_PROCESSING_STREAM, GEMINI_PROCESSING_STREAM]:
        messages = redis_client.xrange(stream, min=job_id, max='+')
        if messages:
            target_stream = stream
            break
            
    if not target_stream:
        print(f"Warning: Job {job_id} not found in any stream")
        return
        
    # Get the original job data
    messages = redis_client.xrange(target_stream, min=job_id, max='+')
    if not messages:
        print(f"Warning: Job {job_id} not found in stream {target_stream}")
        return
        
    # Start from the original job data
    update_data = messages[0][1].copy()
    update_data['status'] = status
    if progress is not None:
        update_data['progress'] = progress
    if result:
        update_data.update(result)
        
    # Delete the old message and add the update
    redis_client.xdel(target_stream, job_id)
    redis_client.xadd(target_stream, update_data) 