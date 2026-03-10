"""
Background Worker

Async worker that processes jobs from the queue.
Runs in a background task alongside the FastAPI server.
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime, timezone

from .queue import JobQueue, Job, JobStatus
from .tasks import TaskRegistry

logger = logging.getLogger(__name__)


class BackgroundWorker:
    """
    Background worker that processes jobs from the queue.
    
    Features:
    - Runs as asyncio background task
    - Processes one job at a time
    - Handles errors gracefully
    - Respects shutdown signals
    """
    
    def __init__(self, db, poll_interval: float = 5.0):
        """
        Initialize the worker.
        
        Args:
            db: Database connection
            poll_interval: Seconds between queue checks when idle
        """
        self.db = db
        self.queue = JobQueue(db)
        self.poll_interval = poll_interval
        self._running = False
        self._current_job: Optional[Job] = None
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the background worker"""
        if self._running:
            logger.warning("Worker already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Background worker started")
    
    async def stop(self):
        """Stop the background worker gracefully"""
        logger.info("Stopping background worker...")
        self._running = False
        
        if self._task:
            # Wait for current job to finish (with timeout)
            try:
                await asyncio.wait_for(self._task, timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning("Worker shutdown timed out, cancelling...")
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
        
        logger.info("Background worker stopped")
    
    async def _run_loop(self):
        """Main worker loop"""
        logger.info("Worker loop started")
        
        # Initialize queue
        await self.queue.initialize()
        
        while self._running:
            try:
                # Try to get a job
                job = await self.queue.dequeue()
                
                if job:
                    self._current_job = job
                    await self._process_job(job)
                    self._current_job = None
                else:
                    # No jobs available, wait before checking again
                    await asyncio.sleep(self.poll_interval)
                    
            except asyncio.CancelledError:
                logger.info("Worker loop cancelled")
                break
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(self.poll_interval)
        
        logger.info("Worker loop ended")
    
    async def _process_job(self, job: Job):
        """Process a single job"""
        logger.info(f"Processing job {job.job_type} (id={job.id})")
        
        try:
            # Get the task function
            task_func = TaskRegistry.get_task(job.job_type)
            
            # Execute the task
            result = await task_func(self.db, job.params)
            
            # Mark as completed
            await self.queue.complete(
                job.id,
                result=result.get('details'),
                records_processed=result.get('records_processed', 0)
            )
            
            logger.info(f"Job {job.job_type} completed successfully")
            
        except ValueError as e:
            # Unknown task type
            await self.queue.fail(job.id, f"Unknown task: {str(e)}")
            
        except Exception as e:
            # Task execution failed
            logger.error(f"Job {job.job_type} failed: {e}")
            await self.queue.fail(job.id, str(e))
    
    @property
    def is_running(self) -> bool:
        """Check if worker is running"""
        return self._running
    
    @property
    def current_job(self) -> Optional[Job]:
        """Get the currently processing job"""
        return self._current_job
    
    def get_status(self) -> dict:
        """Get worker status"""
        return {
            'running': self._running,
            'current_job': self._current_job.to_dict() if self._current_job else None,
            'poll_interval': self.poll_interval,
        }


class WorkerManager:
    """
    Manages multiple worker instances and provides a singleton interface.
    """
    
    _instance: Optional['WorkerManager'] = None
    _worker: Optional[BackgroundWorker] = None
    
    @classmethod
    def get_instance(cls) -> 'WorkerManager':
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, db):
        """Initialize the worker with a database connection"""
        if self._worker is None:
            self._worker = BackgroundWorker(db)
    
    async def start(self):
        """Start the worker"""
        if self._worker:
            await self._worker.start()
    
    async def stop(self):
        """Stop the worker"""
        if self._worker:
            await self._worker.stop()
    
    @property
    def worker(self) -> Optional[BackgroundWorker]:
        """Get the worker instance"""
        return self._worker
    
    def get_status(self) -> dict:
        """Get worker status"""
        if self._worker:
            return self._worker.get_status()
        return {'running': False, 'initialized': False}
