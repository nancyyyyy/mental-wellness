from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat, auth

app = FastAPI(title="Mind Companion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Mind Companion Backend Running"}

@app.get("/health")
async def health():
    return {"status": "ok"}
