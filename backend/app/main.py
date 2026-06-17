from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, chat, practices, insights
from .db.base import engine, Base
from .db.models import Memory
import os

app = FastAPI(title="Mind Companion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_validation():
    print("\n=== Mind Companion Startup Validation ===")
    
    required_vars = ["SECRET_KEY", "DATABASE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
    else:
        print("✅ All required environment variables are set.")

    try:
        Memory.__table__.drop(engine, checkfirst=True)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified/created successfully.")
    except Exception as e:
        print(f"❌ Database error: {e}")

    print("==========================================\n")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(practices.router, prefix="/practices", tags=["Practices"])
app.include_router(insights.router, prefix="/insights", tags=["Insights"])

@app.get("/")
async def root():
    return {"message": "Mind Companion Backend Running"}

@app.get("/health")
async def health():
    return {"status": "ok"}
