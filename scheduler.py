#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scheduler module for huizenzoeker application.
This module provides functionality for scheduling periodic tasks.
"""

import logging
import time
import threading
import schedule
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("huizenzoeker.log"),
        logging.StreamHandler()
    ]
)

class TaskScheduler:
    """Class for scheduling and running periodic tasks."""
    
    def __init__(self):
        """Initialize the task scheduler."""
        self.logger = logging.getLogger("scheduler")
        self.running = False
        self.thread = None
    
    def add_job(self, job: Callable, interval_minutes: int, job_name: str = None) -> None:
        """
        Add a job to run at specified interval.
        
        Args:
            job: Function to run
            interval_minutes: Interval in minutes
            job_name: Optional name for the job (for logging)
        """
        job_name = job_name or job.__name__
        
        # Wrapper to add logging
        def job_wrapper():
            try:
                self.logger.info(f"Running scheduled job: {job_name}")
                start_time = time.time()
                result = job()
                elapsed = time.time() - start_time
                self.logger.info(f"Job {job_name} completed in {elapsed:.2f} seconds")
                return result
            except Exception as e:
                self.logger.error(f"Error in scheduled job {job_name}: {str(e)}")
                return None
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(job_wrapper)
        self.logger.info(f"Added job {job_name} to run every {interval_minutes} minutes")
    
    def add_daily_job(self, job: Callable, time_str: str, job_name: str = None) -> None:
        """
        Add a job to run daily at specified time.
        
        Args:
            job: Function to run
            time_str: Time string in format "HH:MM"
            job_name: Optional name for the job (for logging)
        """
        job_name = job_name or job.__name__
        
        # Wrapper to add logging
        def job_wrapper():
            try:
                self.logger.info(f"Running scheduled daily job: {job_name}")
                start_time = time.time()
                result = job()
                elapsed = time.time() - start_time
                self.logger.info(f"Daily job {job_name} completed in {elapsed:.2f} seconds")
                return result
            except Exception as e:
                self.logger.error(f"Error in scheduled daily job {job_name}: {str(e)}")
                return None
        
        # Schedule the job
        schedule.every().day.at(time_str).do(job_wrapper)
        self.logger.info(f"Added daily job {job_name} to run at {time_str}")
    
    def start(self) -> None:
        """Start the scheduler in a background thread."""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.running = True
        
        def run_scheduler():
            self.logger.info("Scheduler started")
            while self.running:
                schedule.run_pending()
                time.sleep(1)
            self.logger.info("Scheduler stopped")
        
        self.thread = threading.Thread(target=run_scheduler)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self) -> None:
        """Stop the scheduler."""
        if not self.running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.logger.info("Stopping scheduler...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        
        # Clear all scheduled jobs
        schedule.clear()
        self.logger.info("All scheduled jobs cleared")
    
    def run_pending(self) -> None:
        """Run pending jobs (for manual control)."""
        schedule.run_pending()
    
    def get_next_run(self, job_name: str = None) -> Optional[datetime]:
        """
        Get the next run time for a job.
        
        Args:
            job_name: Name of the job (if None, returns next run of any job)
            
        Returns:
            Datetime of next run or None if no jobs scheduled
        """
        jobs = schedule.get_jobs()
        if not jobs:
            return None
        
        if job_name:
            # Find job by name
            for job in jobs:
                if hasattr(job, 'job_func') and hasattr(job.job_func, '__name__') and job.job_func.__name__ == job_name:
                    return job.next_run
            return None
        else:
            # Find next job to run
            return min(jobs, key=lambda job: job.next_run).next_run
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List all scheduled jobs.
        
        Returns:
            List of job dictionaries with name, interval, and next run time
        """
        jobs = schedule.get_jobs()
        result = []
        
        for job in jobs:
            job_info = {
                'name': job.job_func.__name__ if hasattr(job.job_func, '__name__') else 'unknown',
                'interval': str(job.interval),
                'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else 'unknown'
            }
            result.append(job_info)
        
        return result
