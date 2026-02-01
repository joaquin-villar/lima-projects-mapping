
import jwt
from datetime import datetime, timedelta

def generate_admin_token():
    # We use hardcoded role string to avoid import issues in this simple script
    payload = {
        "sub": "admin_user_id",
        "email": "admin@example.com",
        "role": "admin", # UserRole.ADMIN.value
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    
    # Backend currently decodes with verify_signature=False, 
    # so any key works for now. 
    token = jwt.encode(payload, "secret-dev-key", algorithm="HS256")
    return token

if __name__ == "__main__":
    token = generate_admin_token()
    print(token)
