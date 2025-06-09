import pytest
import redis
import os

@pytest.fixture(scope="session")
def redis_client():
    """Create a Redis client for testing."""
    client = redis.Redis(
        host=os.environ.get('REDIS_HOST', 'redis'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        db=0
    )
    yield client
    # Cleanup after tests
    client.flushdb()

@pytest.fixture(scope="session")
def test_pdf_content():
    """Create a simple PDF content for testing."""
    return b'%PDF-1.4\n%Test PDF content' 