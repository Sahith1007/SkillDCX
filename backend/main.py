from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local routers
from routes import certificates, verify, ai_recommender, wallet, contracts, issue

app = FastAPI()

# CORS (open for dev; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(certificates.router, prefix="/certificates", tags=["certificates"])
app.include_router(verify.router, prefix="/verify", tags=["verify"])
app.include_router(issue.router, prefix="/issue", tags=["issue"])
app.include_router(ai_recommender.router)  # mounted at /ai
app.include_router(wallet.router)  # mounted at /wallet
app.include_router(contracts.router)  # mounted at /contracts


@app.get("/")
def root():
    return {"message": "SkillDCX backend is running 🚀"}
