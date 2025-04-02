#
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import yaml
import json
import os
from datetime import datetime
import sys

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import other modules
from api.endpoints import router as endpoints_router
from scripts.data_drift import check_data_drift
from scripts.model_drift import check_model_drift
from scripts.performance import calculate_metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "api.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# Load configuration
def load_config():
    try:
        with open("config/monitor_config.yaml", "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        return {}


config = load_config()


# Define data models


# Create FastAPI application
app = FastAPI(
    title="MLOps Monitor API",
    description="MLOps monitoring system API supporting continuous monitoring, drift detection, and performance evaluation",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(endpoints_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Version information
@app.get("/version")
async def version():
    try:
        with open("VERSION", "r") as file:
            version = file.read().strip()
        return {"version": version}
    except:
        return {"version": "unknown"}


# Record prediction
@app.post("/api/v1/predictions")


# Record feedback
@app.post("/api/v1/feedback")


# Get configuration
@app.get("/api/v1/config")
async def get_config():
    return config


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("API service started")
    # Ensure required directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("feedback_data/predictions", exist_ok=True)
    os.makedirs("feedback_data/actual_outcomes", exist_ok=True)
    os.makedirs("feedback_data/drift_reports", exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API service shutting down")


# Main entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
