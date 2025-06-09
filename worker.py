import json
import time
import os
from services.gemini_service import setup_gemini, generate_markdown_and_summary
from services.redis_service import redis_client, TEXT_PROCESSING_STREAM

# Setup Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', "AIzaSyCVBj8XTXuOkClPEk_HXSpk30nPxudRQGo")
if GEMINI_API_KEY:
    setup_gemini(GEMINI_API_KEY)
    print("✓ Gemini API setup completed successfully")
else:
    print("⚠ Warning: GEMINI_API_KEY environment variable not set. Text summarization will not work.")

# Constants
RATE_LIMIT_DELAY = 35  # base delay in seconds
MAX_RETRIES = 3
MAX_RATE_LIMIT_DELAY = 120  # maximum delay in seconds

def get_next_delay(retry_count):
    """Calculate exponential backoff delay with jitter."""
    base_delay = RATE_LIMIT_DELAY * (2 ** retry_count)  # exponential backoff
    jitter = base_delay * 0.1  # 10% jitter
    delay = min(base_delay + jitter, MAX_RATE_LIMIT_DELAY)
    return delay

def process_text_job(job_id: str, job_data: dict):
    """Process a text job using Gemini for summarization."""
    print(f"\n==================================================")
    print(f"Processing text job {job_id}")
    print(f"Input text: {job_data['text']}")
    
    # Set initial processing status
    result_key = f"text_summary:{job_id}"
    redis_client.hset(result_key, mapping={
        'text': job_data['text'],
        'status': 'processing',
        'retry_count': '0'
    })
    
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            print("\nCalling Gemini API for summarization...")
            # Generate summary using Gemini
            _, summary = generate_markdown_and_summary(job_data['text'])
            
            # Store the result in Redis
            redis_client.hset(result_key, mapping={
                'text': job_data['text'],
                'summary': summary,
                'status': 'completed',
                'retry_count': str(retry_count)
            })
            
            print(f"✅ Successfully processed job {job_id}")
            print("Waiting 10 seconds before processing next job...")
            time.sleep(10)  # Wait 10 seconds after completing a job
            return
            
        except Exception as e:
            retry_count += 1
            error_msg = str(e)
            print(f"❌ Error processing job {job_id}: {error_msg}")
            
            if "429" in error_msg and retry_count < MAX_RETRIES:
                delay = get_next_delay(retry_count)
                print(f"Rate limit hit. Waiting {delay:.1f} seconds before retry {retry_count + 1}/{MAX_RETRIES}...")
                # Update status to show retry count
                redis_client.hset(result_key, mapping={
                    'text': job_data['text'],
                    'status': 'processing',
                    'error': error_msg,
                    'retry_count': str(retry_count)
                })
                time.sleep(delay)
                continue
            
            # Store the error in Redis
            redis_client.hset(result_key, mapping={
                'text': job_data['text'],
                'error': error_msg,
                'status': 'failed',
                'retry_count': str(retry_count)
            })
            break

def should_process_message(msg_id: str) -> bool:
    """Check if a message should be processed based on its current status."""
    summary_data = redis_client.hgetall(f"text_summary:{msg_id}")
    if not summary_data:
        return True  # No summary data exists, should process
    
    status = summary_data.get(b'status', b'').decode('utf-8')
    return status != 'completed'  # Only process if not completed

def main():
    """Main worker loop."""
    print("\nStarting text processing worker...")
    print("Waiting for messages in stream:", TEXT_PROCESSING_STREAM)
    
    # Test Redis connection
    try:
        redis_client.ping()
        print("✓ Successfully connected to Redis")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {str(e)}")
        return

    while True:
        try:
            print("\nScanning all messages in stream...")
            # Get all messages in the stream
            all_messages = redis_client.xrange(TEXT_PROCESSING_STREAM, min='-', max='+')
            print(f"Found {len(all_messages)} messages in stream.")
            for msg_id, msg_data in all_messages:
                msg_id_str = msg_id.decode('utf-8') if isinstance(msg_id, bytes) else msg_id
                summary_data = redis_client.hgetall(f"text_summary:{msg_id_str}")
                status = summary_data.get(b'status', b'').decode('utf-8') if summary_data else None
                
                if status != 'completed':
                    print(f"Processing message {msg_id_str} (status: {status})")
                    try:
                        text = json.loads(msg_data[b'text'].decode('utf-8'))
                        process_text_job(msg_id_str, {'text': text})
                    except Exception as e:
                        print(f"❌ Error processing message {msg_id_str}: {str(e)}")
                else:
                    print(f"Skipping message {msg_id_str} (already completed)")
            print("Sleeping for 5 seconds before next scan...")
            time.sleep(5)
        except Exception as e:
            print(f"\n❌ Error in worker loop: {str(e)}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main() 