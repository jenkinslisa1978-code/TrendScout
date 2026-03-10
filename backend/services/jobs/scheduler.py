"""
Job Scheduler

APScheduler-based scheduler for automatic job execution.
Supports cron-style scheduling with timezone awareness.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from .queue import JobQueue, TriggerSource
from .tasks import TaskRegistry

logger = logging.getLogger(__name__)


class JobScheduler:
    """
    Scheduler for automatic job execution.
    
    Features:
    - Cron-style scheduling
    - Timezone aware (UTC)
    - Auto-registers scheduled tasks
    - Event logging
    """
    
    def __init__(self, db):
        """
        Initialize the scheduler.
        
        Args:
            db: Database connection
        """
        self.db = db
        self.queue = JobQueue(db)
        self.scheduler = AsyncIOScheduler(timezone='UTC')
        self._started = False
        
        # Register event listeners
        self.scheduler.add_listener(
            self._on_job_executed, 
            EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(
            self._on_job_error, 
            EVENT_JOB_ERROR
        )
    
    async def start(self):
        """Start the scheduler and register all scheduled tasks"""
        if self._started:
            logger.warning("Scheduler already started")
            return
        
        # Initialize queue
        await self.queue.initialize()
        
        # Register all scheduled tasks
        scheduled_tasks = TaskRegistry.get_scheduled_tasks()
        
        for task in scheduled_tasks:
            self._register_scheduled_task(
                task['name'],
                task['schedule']
            )
        
        # Start the scheduler
        self.scheduler.start()
        self._started = True
        
        logger.info(f"Scheduler started with {len(scheduled_tasks)} scheduled tasks")
    
    async def stop(self):
        """Stop the scheduler"""
        if self._started:
            self.scheduler.shutdown(wait=False)
            self._started = False
            logger.info("Scheduler stopped")
    
    def _register_scheduled_task(self, task_name: str, cron_expression: str):
        """
        Register a task with cron scheduling.
        
        Args:
            task_name: Name of the task to schedule
            cron_expression: Cron expression (e.g., "0 */4 * * *")
        """
        # Parse cron expression
        # Format: minute hour day month day_of_week
        parts = cron_expression.split()
        
        if len(parts) != 5:
            logger.error(f"Invalid cron expression for {task_name}: {cron_expression}")
            return
        
        trigger = CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
            timezone='UTC'
        )
        
        # Add job to scheduler
        self.scheduler.add_job(
            self._enqueue_task,
            trigger,
            args=[task_name],
            id=f"scheduled_{task_name}",
            name=f"Scheduled: {task_name}",
            replace_existing=True,
            coalesce=True,  # Combine missed runs
            max_instances=1,  # Prevent concurrent runs
        )
        
        logger.info(f"Registered scheduled task: {task_name} ({cron_expression})")
    
    async def _enqueue_task(self, task_name: str):
        """Enqueue a task from the scheduler"""
        logger.info(f"Scheduler triggering task: {task_name}")
        
        job = await self.queue.enqueue(
            job_type=task_name,
            trigger_source=TriggerSource.SCHEDULED,
            allow_duplicate=False
        )
        
        if job:
            logger.info(f"Scheduled task enqueued: {task_name} (job_id={job.id})")
        else:
            logger.warning(f"Scheduled task skipped (duplicate): {task_name}")
    
    def _on_job_executed(self, event):
        """Handle job executed event"""
        logger.debug(f"Scheduler job executed: {event.job_id}")
    
    def _on_job_error(self, event):
        """Handle job error event"""
        logger.error(f"Scheduler job error: {event.job_id} - {event.exception}")
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs with their next run times"""
        jobs = []
        
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': next_run.isoformat() if next_run else None,
                'trigger': str(job.trigger),
            })
        
        return jobs
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'running': self._started,
            'scheduled_jobs': len(self.scheduler.get_jobs()),
            'jobs': self.get_scheduled_jobs(),
        }
    
    def pause_job(self, task_name: str) -> bool:
        """Pause a scheduled job"""
        job_id = f"scheduled_{task_name}"
        job = self.scheduler.get_job(job_id)
        
        if job:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused scheduled job: {task_name}")
            return True
        return False
    
    def resume_job(self, task_name: str) -> bool:
        """Resume a paused scheduled job"""
        job_id = f"scheduled_{task_name}"
        job = self.scheduler.get_job(job_id)
        
        if job:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed scheduled job: {task_name}")
            return True
        return False
    
    async def trigger_now(self, task_name: str, params: Dict[str, Any] = None) -> Optional[str]:
        """
        Manually trigger a task to run immediately.
        
        Args:
            task_name: Name of the task to trigger
            params: Optional parameters to pass to the task
            
        Returns:
            Job ID if enqueued, None if skipped
        """
        job = await self.queue.enqueue(
            job_type=task_name,
            trigger_source=TriggerSource.MANUAL,
            params=params or {},
            allow_duplicate=False
        )
        
        if job:
            return job.id
        return None


class SchedulerManager:
    """
    Singleton manager for the job scheduler.
    """
    
    _instance: Optional['SchedulerManager'] = None
    _scheduler: Optional[JobScheduler] = None
    
    @classmethod
    def get_instance(cls) -> 'SchedulerManager':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, db):
        """Initialize the scheduler with a database connection"""
        if self._scheduler is None:
            self._scheduler = JobScheduler(db)
    
    async def start(self):
        """Start the scheduler"""
        if self._scheduler:
            await self._scheduler.start()
    
    async def stop(self):
        """Stop the scheduler"""
        if self._scheduler:
            await self._scheduler.stop()
    
    @property
    def scheduler(self) -> Optional[JobScheduler]:
        """Get the scheduler instance"""
        return self._scheduler
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        if self._scheduler:
            return self._scheduler.get_status()
        return {'running': False, 'initialized': False}
