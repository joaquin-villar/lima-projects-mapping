
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

def test_api_delete(project_id, token):
    url = f"http://127.0.0.1:8000/api/projects/{project_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print(f"Sending DELETE request to {url}")
        with httpx.Client() as client:
            response = client.delete(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Get token from generate_token script logic
    import jwt
    from datetime import datetime, timedelta
    CLIENT_KEY = os.getenv("NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY", "your-fallback-public-key")
    payload = {
        "sub": "admin_test",
        "email": "admin@test.com",
        "role": "admin",
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, CLIENT_KEY, algorithm="HS256")
    
    # Try to delete project 6
    test_api_delete(6, token)
