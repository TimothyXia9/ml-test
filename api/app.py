#
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import yaml
import json
import os
from datetime import datetime
from pydantic import BaseModel, Field
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
class Prediction(BaseModel):
    model_version: str = Field(..., description="Model version")
    prediction: float = Field(..., description="Model prediction value")
    features: dict = Field(..., description="Input features")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Prediction timestamp"
    )
    metadata: dict = Field(default={}, description="Additional metadata")


class Feedback(BaseModel):
    prediction_id: str = Field(..., description="Prediction ID")
    actual_value: float = Field(..., description="Actual value")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Feedback timestamp"
    )
    metadata: dict = Field(default={}, description="Additional metadata")


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
async def record_prediction(prediction: Prediction, background_tasks: BackgroundTasks):
    try:
        # Generate unique ID
        prediction_id = (
            f"{prediction.model_version}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        # Save prediction
        prediction_data = prediction.dict()
        prediction_data["id"] = prediction_id

        # Ensure directory exists
        os.makedirs("feedback_data/predictions", exist_ok=True)

        # Save prediction data
        prediction_file = f"feedback_data/predictions/{prediction_id}.json"
        with open(prediction_file, "w") as f:
            json.dump(prediction_data, f)

        # Asynchronously check for data drift
        background_tasks.add_task(check_data_drift, prediction.features)

        logger.info(f"Recorded prediction: {prediction_id}")
        return {"prediction_id": prediction_id, "status": "recorded"}

    except Exception as e:
        logger.error(f"Failed to record prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Record feedback
@app.post("/api/v1/feedback")
async def record_feedback(feedback: Feedback, background_tasks: BackgroundTasks):
    try:
        # Check if prediction exists
        prediction_file = f"feedback_data/predictions/{feedback.prediction_id}.json"
        if not os.path.exists(prediction_file):
            raise HTTPException(status_code=404, detail="Prediction ID not found")

        # Load prediction data
        with open(prediction_file, "r") as f:
            prediction_data = json.load(f)

        # Ensure directory exists
        os.makedirs("feedback_data/actual_outcomes", exist_ok=True)

        # Save feedback data
        feedback_data = feedback.dict()
        feedback_file = f"feedback_data/actual_outcomes/{feedback.prediction_id}.json"
        with open(feedback_file, "w") as f:
            json.dump(feedback_data, f)

        # Asynchronously check model drift and calculate performance metrics
        background_tasks.add_task(check_model_drift, prediction_data, feedback_data)
        background_tasks.add_task(calculate_metrics, prediction_data, feedback_data)

        logger.info(f"Recorded feedback: {feedback.prediction_id}")
        return {"status": "feedback recorded"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
