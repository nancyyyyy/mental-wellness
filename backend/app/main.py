from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, chat, practices
from .db.base import engine, Base

app = FastAPI(title="Mind Companion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup (including memories table)
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified successfully.")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(practices.router, prefix="/practices", tags=["Practices"])

@app.get("/")
async def root():
    return {"message": "Mind Companion Backend Running"}

@app.get("/health")
async def health():
    return {"status": "ok"}
