from fastapi import APIRouter, HTTPException, Request, Depends, Header, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import uuid
import json
import logging
import re

from auth import get_current_user, get_optional_user, AuthenticatedUser
from common.database import db
from common.cache import get_cached, set_cached, slugify, get_margin_range
from common.helpers import (
    get_user_plan, require_plan, require_admin, build_winning_reasons,
    track_product_store_created, track_product_exported, run_automation_on_products,
)
from common.scoring import (
    calculate_trend_score, calculate_trend_stage, calculate_opportunity_rating,
    generate_ai_summary, calculate_early_trend_score, calculate_market_score,
    calculate_launch_score, generate_mock_competitor_data, calculate_success_probability,
    should_generate_alert, generate_alert, run_full_automation, generate_early_trend_alert,
    should_generate_early_trend_alert,
)
from common.models import *

jobs_router = APIRouter(prefix="/api/jobs")

@jobs_router.get("/status")
async def get_jobs_status():
    """
    Get overall status of the background job system.
    Shows worker status, scheduler status, and queue statistics.
    """
    try:
        from services.jobs.queue import JobQueue
        from services.jobs.worker import WorkerManager
        from services.jobs.scheduler import SchedulerManager
        from services.jobs.tasks import TaskRegistry
        
        queue = JobQueue(db)
        queue_stats = await queue.get_queue_stats()
        
        worker_manager = WorkerManager.get_instance()
        scheduler_manager = SchedulerManager.get_instance()
        
        return {
            "worker": worker_manager.get_status(),
            "scheduler": scheduler_manager.get_status(),
            "queue": queue_stats,
            "available_tasks": TaskRegistry.get_all_tasks(),
        }
    except Exception as e:
        logging.error(f"Jobs status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.get("/history")
async def get_job_history(
    job_type: Optional[str] = None,
    limit: int = 50
):
    """
    Get job execution history.
    Shows completed, failed, and running jobs.
    """
    try:
        from services.jobs.queue import JobQueue
        
        queue = JobQueue(db)
        jobs = await queue.get_job_history(job_type=job_type, limit=limit)
        
        return {
            "jobs": [j.to_dict() for j in jobs],
            "count": len(jobs),
        }
    except Exception as e:
        logging.error(f"Job history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.get("/running")
async def get_running_jobs():
    """Get currently running jobs"""
    try:
        from services.jobs.queue import JobQueue
        
        queue = JobQueue(db)
        running = await queue.get_running_jobs()
        pending = await queue.get_pending_jobs(limit=20)
        
        return {
            "running": [j.to_dict() for j in running],
            "pending": [j.to_dict() for j in pending],
            "running_count": len(running),
            "pending_count": len(pending),
        }
    except Exception as e:
        logging.error(f"Running jobs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.get("/{job_id}")
async def get_job_details(job_id: str):
    """Get details of a specific job"""
    try:
        from services.jobs.queue import JobQueue
        
        queue = JobQueue(db)
        job = await queue.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Job details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.post("/trigger/{task_name}")
async def trigger_job(
    task_name: str,
    params: Optional[Dict[str, Any]] = None
):
    """
    Manually trigger a background job.
    
    Available tasks:
    - ingest_trending_products
    - update_market_scores
    - update_competitor_data
    - update_ad_activity
    - update_supplier_data
    - generate_alerts
    - full_pipeline
    - cleanup_stale_jobs
    """
    try:
        from services.jobs.queue import JobQueue, TriggerSource
        from services.jobs.tasks import TaskRegistry
        
        # Validate task exists
        available_tasks = TaskRegistry.get_all_tasks()
        if task_name not in available_tasks:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown task: {task_name}. Available: {list(available_tasks.keys())}"
            )
        
        queue = JobQueue(db)
        job = await queue.enqueue(
            job_type=task_name,
            trigger_source=TriggerSource.MANUAL,
            params=params or {},
            allow_duplicate=False
        )
        
        if job:
            return {
                "success": True,
                "message": f"Job {task_name} enqueued",
                "job_id": job.id,
                "status": job.status.value,
            }
        else:
            return {
                "success": False,
                "message": f"Job {task_name} already running or pending",
                "job_id": None,
            }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Trigger job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a pending job"""
    try:
        from services.jobs.queue import JobQueue
        
        queue = JobQueue(db)
        cancelled = await queue.cancel(job_id)
        
        if cancelled:
            return {"success": True, "message": "Job cancelled"}
        else:
            return {"success": False, "message": "Job not found or already running"}
    except Exception as e:
        logging.error(f"Cancel job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.get("/scheduled/list")
async def get_scheduled_jobs():
    """Get all scheduled jobs with their next run times"""
    try:
        from services.jobs.scheduler import SchedulerManager
        
        scheduler_manager = SchedulerManager.get_instance()
        if scheduler_manager.scheduler:
            return {
                "scheduled_jobs": scheduler_manager.scheduler.get_scheduled_jobs(),
                "scheduler_running": scheduler_manager.get_status()['running'],
            }
        else:
            return {
                "scheduled_jobs": [],
                "scheduler_running": False,
            }
    except Exception as e:
        logging.error(f"Scheduled jobs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.post("/scheduled/{task_name}/pause")
async def pause_scheduled_job(task_name: str):
    """Pause a scheduled job"""
    try:
        from services.jobs.scheduler import SchedulerManager
        
        scheduler_manager = SchedulerManager.get_instance()
        if scheduler_manager.scheduler:
            paused = scheduler_manager.scheduler.pause_job(task_name)
            if paused:
                return {"success": True, "message": f"Scheduled job {task_name} paused"}
        
        return {"success": False, "message": f"Scheduled job {task_name} not found"}
    except Exception as e:
        logging.error(f"Pause job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@jobs_router.post("/scheduled/{task_name}/resume")
async def resume_scheduled_job(task_name: str):
    """Resume a paused scheduled job"""
    try:
        from services.jobs.scheduler import SchedulerManager
        
        scheduler_manager = SchedulerManager.get_instance()
        if scheduler_manager.scheduler:
            resumed = scheduler_manager.scheduler.resume_job(task_name)
            if resumed:
                return {"success": True, "message": f"Scheduled job {task_name} resumed"}
        
        return {"success": False, "message": f"Scheduled job {task_name} not found"}
    except Exception as e:
        logging.error(f"Resume job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# ROUTES - Viral Growth & Referrals
# =====================



routers = [jobs_router]
