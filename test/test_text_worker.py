import requests

API_URL = "http://localhost:8000/process-text/"

def test_process_text():
    payload = {"text": "Hello from the test worker script!"}
    response = requests.post(API_URL, json=payload)
    print("Status code:", response.status_code)
    print("Response:", response.json())

if __name__ == "__main__":
    test_process_text() 