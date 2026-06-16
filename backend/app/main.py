from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, chat, practices

app = FastAPI(title="Mind Companion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(practices.router, prefix="/practices", tags=["Practices"])

@app.get("/")
def root():
    return {"message": "Mind Companion API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}