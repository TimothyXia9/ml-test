#!/bin/bash
set -e

echo "Starting MLOps Monitor container..."

mkdir -p /app/logs
mkdir -p /app/feedback_data/actual_outcomes
mkdir -p /app/feedback_data/drift_reports
mkdir -p /app/feedback_data/predictions


# chmod -R 755 /app/logs
# chmod -R 755 /app/feedback_data

cd /app
export PYTHONPATH=/app

if [ "$1" = "api" ]; then
    # 如果指定了API模式，启动API服务
    uvicorn api.app:app --host 0.0.0.0 --port 8000
elif [ "$1" = "dashboard" ]; then
    python -m dashboards.metrics_dashboard
else
    # python -m scripts.collect_metrics &
    
    # python -m scripts.data_drift &
    
    # python -m scripts.model_drift &
    
    # python -m scripts.performance &
    
    # python -m scripts.alert_manager &
    
    uvicorn api.app:app --host 0.0.0.0 --port 8000
fi

tail -f /dev/null