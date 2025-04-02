from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
import os

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/api/v1",
    tags=["endpoints"],
    responses={404: {"description": "Not found"}},
)


# 定义模型
class MetricQuery(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    model_version: Optional[str] = None
    metric_names: Optional[List[str]] = None


class AlertConfig(BaseModel):
    metric_name: str
    threshold: float
    condition: str  # "greater_than", "less_than", "equal_to"
    severity: str  # "low", "medium", "high"


# API端点
@router.get("/metrics")
async def get_metrics(query: MetricQuery = Depends()):
    """
    获取性能指标数据
    """
    try:
        # 在实际应用中，这里会查询存储的指标数据
        # 简化示例，返回一些模拟数据
        return {
            "metrics": [
                {
                    "name": "accuracy",
                    "value": 0.95,
                    "timestamp": datetime.now().isoformat(),
                },
                {
                    "name": "f1_score",
                    "value": 0.92,
                    "timestamp": datetime.now().isoformat(),
                },
            ]
        }
    except Exception as e:
        logger.error(f"获取指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drift/data")
async def get_data_drift():
    """
    获取数据漂移报告
    """
    try:
        # 检查是否有漂移报告
        reports_dir = "feedback_data/drift_reports"
        if not os.path.exists(reports_dir):
            return {"data_drift": []}

        # 获取最新的漂移报告
        reports = os.listdir(reports_dir)
        if not reports:
            return {"data_drift": []}

        # 按修改时间排序，获取最新报告
        latest_report = max(
            reports, key=lambda x: os.path.getmtime(os.path.join(reports_dir, x))
        )

        with open(os.path.join(reports_dir, latest_report), "r") as f:
            drift_data = json.load(f)

        return {"data_drift": drift_data}
    except Exception as e:
        logger.error(f"获取数据漂移失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drift/model")
async def get_model_drift():
    """
    获取模型漂移数据
    """
    try:
        # 实际应用中，这里会查询存储的模型漂移数据
        return {
            "model_drift": [
                {
                    "feature": "importance_shift",
                    "current_value": 0.05,
                    "threshold": 0.1,
                    "status": "normal",
                },
                {
                    "feature": "prediction_distribution",
                    "current_value": 0.12,
                    "threshold": 0.1,
                    "status": "drifting",
                },
            ]
        }
    except Exception as e:
        logger.error(f"获取模型漂移失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts():
    """
    获取当前告警
    """
    try:
        # 实际应用中，这里会查询存储的告警数据
        return {
            "alerts": [
                {
                    "id": "alert-001",
                    "metric": "accuracy",
                    "value": 0.89,
                    "threshold": 0.9,
                    "condition": "less_than",
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "status": "active",
                }
            ]
        }
    except Exception as e:
        logger.error(f"获取告警失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/config")
async def set_alert_config(config: AlertConfig):
    """
    配置告警规则
    """
    try:
        # 实际应用中，这里会保存告警配置
        return {
            "status": "success",
            "message": f"告警 {config.metric_name} 配置成功",
            "config": config.dict(),
        }
    except Exception as e:
        logger.error(f"配置告警失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status():
    """
    获取系统状态
    """
    try:
        return {
            "status": "operational",
            "components": {
                "api": "healthy",
                "data_drift": "healthy",
                "model_drift": "healthy",
                "alerts": "healthy",
                "feedback_loop": "healthy",
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
