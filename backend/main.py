from fastapi import FastAPI
from routes import certificates, verify

app = FastAPI()
from routes import certificates
app.include_router(certificates.router)


app.include_router(certificates.router, prefix="/certificates", tags=["certificates"])
app.include_router(verify.router, prefix="/verify", tags=["verify"])

@app.get("/")
def root():
    return {"message": "SkillDCX backend is running 🚀"}
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
