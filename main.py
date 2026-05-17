from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables FIRST before importing routers
load_dotenv()

from app.routers import bot, risk_checker, report, news

# Create FastAPI app
app = FastAPI(
    title="Cyber Buddy API",
    description="A comprehensive cybersecurity platform API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bot.router, prefix="/api/bot", tags=["Bot"])
app.include_router(risk_checker.router, prefix="/api/risk-checker", tags=["Risk Checker"])
app.include_router(report.router, prefix="/api/report", tags=["Report"])
app.include_router(news.router, prefix="/api/news", tags=["News"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to Cyber Buddy API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Cyber Buddy API is running"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
