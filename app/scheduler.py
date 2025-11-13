"""
Scheduler for running health checks periodically
"""
from apscheduler.schedulers.background import BackgroundScheduler
from app.health_checker import HealthChecker


class HealthCheckScheduler:
    """Scheduler for periodic health checks"""
    
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        
    def init_app(self, app):
        """Initialize scheduler with Flask app"""
        self.app = app
        
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            # Schedule health checks every minute
            self.scheduler.add_job(
                func=lambda: HealthChecker.check_all_endpoints(self.app),
                trigger='interval',
                seconds=60,
                id='health_check_job',
                name='Check all endpoints',
                replace_existing=True
            )
            self.scheduler.start()
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
