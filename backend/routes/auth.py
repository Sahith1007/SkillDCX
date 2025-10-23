from fastapi import HTTPException


# Dummy user for MVP
def get_current_user():
    user = {"username": "university1", "role": "issuer"}
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
