"""
Job Queue Manager

MongoDB-backed job queue with:
- Job persistence
- Status tracking
- Concurrent execution prevention
- Job history and logging
"""

import uuid
import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerSource(str, Enum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    API = "api"


@dataclass
class Job:
    """Represents a background job"""
    id: str
    job_type: str
    status: JobStatus
    trigger_source: TriggerSource
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    records_processed: int = 0
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'job_type': self.job_type,
            'status': self.status.value if isinstance(self.status, JobStatus) else self.status,
            'trigger_source': self.trigger_source.value if isinstance(self.trigger_source, TriggerSource) else self.trigger_source,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'params': self.params,
            'result': self.result,
            'error': self.error,
            'records_processed': self.records_processed,
            'duration_seconds': self.duration_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        return cls(
            id=data['id'],
            job_type=data['job_type'],
            status=JobStatus(data['status']) if isinstance(data['status'], str) else data['status'],
            trigger_source=TriggerSource(data['trigger_source']) if isinstance(data['trigger_source'], str) else data['trigger_source'],
            created_at=data['created_at'],
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
            params=data.get('params', {}),
            result=data.get('result'),
            error=data.get('error'),
            records_processed=data.get('records_processed', 0),
            duration_seconds=data.get('duration_seconds', 0.0),
        )


class JobQueue:
    """
    MongoDB-backed job queue manager.
    
    Features:
    - Enqueue jobs with deduplication
    - Prevent concurrent runs of same job type
    - Track job history and status
    - Support both scheduled and manual triggers
    """
    
    # Collection name for jobs
    COLLECTION = 'background_jobs'
    
    # Lock timeout - if a job is running for longer, consider it stale
    LOCK_TIMEOUT_MINUTES = 30
    
    def __init__(self, db):
        self.db = db
        self._initialized = False
    
    async def initialize(self):
        """Create indexes for job queue"""
        if self._initialized:
            return
        
        collection = self.db[self.COLLECTION]
        
        # Index for finding running jobs by type
        await collection.create_index([("job_type", 1), ("status", 1)])
        
        # Index for finding pending jobs
        await collection.create_index([("status", 1), ("created_at", 1)])
        
        # Index for job history lookup
        await collection.create_index([("created_at", -1)])
        
        # TTL index to auto-delete old completed jobs (keep 7 days)
        await collection.create_index(
            [("completed_at", 1)], 
            expireAfterSeconds=7 * 24 * 60 * 60,
            partialFilterExpression={"status": {"$in": ["completed", "failed", "cancelled"]}}
        )
        
        self._initialized = True
        logger.info("Job queue indexes created")
    
    async def enqueue(
        self, 
        job_type: str, 
        trigger_source: TriggerSource = TriggerSource.MANUAL,
        params: Dict[str, Any] = None,
        allow_duplicate: bool = False
    ) -> Optional[Job]:
        """
        Enqueue a new job.
        
        Args:
            job_type: Type of job to run
            trigger_source: How the job was triggered
            params: Optional parameters for the job
            allow_duplicate: If False, won't enqueue if same job type is running/pending
            
        Returns:
            Job if enqueued, None if duplicate prevented
        """
        await self.initialize()
        
        # Check for existing running/pending job of same type
        if not allow_duplicate:
            existing = await self._get_active_job(job_type)
            if existing:
                logger.warning(f"Job {job_type} already active (id={existing.id}), skipping")
                return None
        
        # Create new job
        job = Job(
            id=str(uuid.uuid4()),
            job_type=job_type,
            status=JobStatus.PENDING,
            trigger_source=trigger_source,
            created_at=datetime.now(timezone.utc).isoformat(),
            params=params or {},
        )
        
        # Insert into database
        await self.db[self.COLLECTION].insert_one(job.to_dict())
        
        logger.info(f"Enqueued job {job.job_type} (id={job.id}, trigger={trigger_source.value})")
        return job
    
    async def dequeue(self) -> Optional[Job]:
        """
        Get the next pending job and mark it as running.
        
        Returns:
            Job if one is available, None otherwise
        """
        await self.initialize()
        
        # Find oldest pending job
        result = await self.db[self.COLLECTION].find_one_and_update(
            {"status": JobStatus.PENDING.value},
            {
                "$set": {
                    "status": JobStatus.RUNNING.value,
                    "started_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            sort=[("created_at", 1)],
            return_document=True
        )
        
        if result:
            # Remove MongoDB _id
            result.pop('_id', None)
            return Job.from_dict(result)
        
        return None
    
    async def complete(
        self, 
        job_id: str, 
        result: Dict[str, Any] = None,
        records_processed: int = 0
    ):
        """Mark a job as completed"""
        now = datetime.now(timezone.utc)
        
        # Calculate duration
        job = await self.get_job(job_id)
        duration = 0.0
        if job and job.started_at:
            started = datetime.fromisoformat(job.started_at.replace('Z', '+00:00'))
            duration = (now - started).total_seconds()
        
        await self.db[self.COLLECTION].update_one(
            {"id": job_id},
            {
                "$set": {
                    "status": JobStatus.COMPLETED.value,
                    "completed_at": now.isoformat(),
                    "result": result,
                    "records_processed": records_processed,
                    "duration_seconds": round(duration, 2),
                }
            }
        )
        
        logger.info(f"Job {job_id} completed: {records_processed} records in {duration:.2f}s")
    
    async def fail(self, job_id: str, error: str):
        """Mark a job as failed"""
        now = datetime.now(timezone.utc)
        
        # Calculate duration
        job = await self.get_job(job_id)
        duration = 0.0
        if job and job.started_at:
            started = datetime.fromisoformat(job.started_at.replace('Z', '+00:00'))
            duration = (now - started).total_seconds()
        
        await self.db[self.COLLECTION].update_one(
            {"id": job_id},
            {
                "$set": {
                    "status": JobStatus.FAILED.value,
                    "completed_at": now.isoformat(),
                    "error": error,
                    "duration_seconds": round(duration, 2),
                }
            }
        )
        
        logger.error(f"Job {job_id} failed: {error}")
    
    async def cancel(self, job_id: str):
        """Cancel a pending job"""
        result = await self.db[self.COLLECTION].update_one(
            {"id": job_id, "status": JobStatus.PENDING.value},
            {
                "$set": {
                    "status": JobStatus.CANCELLED.value,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Job {job_id} cancelled")
            return True
        return False
    
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID"""
        result = await self.db[self.COLLECTION].find_one(
            {"id": job_id},
            {"_id": 0}
        )
        
        if result:
            return Job.from_dict(result)
        return None
    
    async def get_pending_jobs(self, limit: int = 100) -> List[Job]:
        """Get all pending jobs"""
        cursor = self.db[self.COLLECTION].find(
            {"status": JobStatus.PENDING.value},
            {"_id": 0}
        ).sort("created_at", 1).limit(limit)
        
        jobs = await cursor.to_list(limit)
        return [Job.from_dict(j) for j in jobs]
    
    async def get_running_jobs(self) -> List[Job]:
        """Get all running jobs"""
        cursor = self.db[self.COLLECTION].find(
            {"status": JobStatus.RUNNING.value},
            {"_id": 0}
        )
        
        jobs = await cursor.to_list(100)
        return [Job.from_dict(j) for j in jobs]
    
    async def get_job_history(
        self, 
        job_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Job]:
        """Get job history, optionally filtered by type"""
        query = {}
        if job_type:
            query["job_type"] = job_type
        
        cursor = self.db[self.COLLECTION].find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit)
        
        jobs = await cursor.to_list(limit)
        return [Job.from_dict(j) for j in jobs]
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        cursor = self.db[self.COLLECTION].aggregate(pipeline)
        results = await cursor.to_list(10)
        
        stats = {status.value: 0 for status in JobStatus}
        for r in results:
            stats[r['_id']] = r['count']
        
        return {
            "pending": stats.get("pending", 0),
            "running": stats.get("running", 0),
            "completed": stats.get("completed", 0),
            "failed": stats.get("failed", 0),
            "cancelled": stats.get("cancelled", 0),
            "total": sum(stats.values()),
        }
    
    async def _get_active_job(self, job_type: str) -> Optional[Job]:
        """Check if a job of this type is already running or pending"""
        # Check for running jobs
        running = await self.db[self.COLLECTION].find_one(
            {
                "job_type": job_type,
                "status": {"$in": [JobStatus.RUNNING.value, JobStatus.PENDING.value]}
            },
            {"_id": 0}
        )
        
        if running:
            # Check if running job is stale (exceeded timeout)
            if running['status'] == JobStatus.RUNNING.value and running.get('started_at'):
                started = datetime.fromisoformat(running['started_at'].replace('Z', '+00:00'))
                if datetime.now(timezone.utc) - started > timedelta(minutes=self.LOCK_TIMEOUT_MINUTES):
                    # Mark stale job as failed
                    await self.fail(running['id'], "Job timed out (stale lock)")
                    return None
            
            return Job.from_dict(running)
        
        return None
    
    async def cleanup_stale_jobs(self):
        """Mark stale running jobs as failed"""
        timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=self.LOCK_TIMEOUT_MINUTES)
        
        result = await self.db[self.COLLECTION].update_many(
            {
                "status": JobStatus.RUNNING.value,
                "started_at": {"$lt": timeout_threshold.isoformat()}
            },
            {
                "$set": {
                    "status": JobStatus.FAILED.value,
                    "error": "Job timed out (stale lock cleanup)",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            }
        )
        
        if result.modified_count > 0:
            logger.warning(f"Cleaned up {result.modified_count} stale jobs")
        
        return result.modified_count
