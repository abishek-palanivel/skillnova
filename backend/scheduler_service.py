#!/usr/bin/env python3
"""
Scheduler Service for SkillNova
Handles automated tasks like weekly evaluation generation
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from weekly_evaluation_service import weekly_evaluation_service
from models import db, WeeklyEvaluation

class SchedulerService:
    """Service for handling scheduled tasks"""
    
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if self.running:
            print("Scheduler is already running")
            return
        
        self.running = True
        
        # Schedule weekly evaluation generation every Sunday at 5:00 PM
        schedule.every().sunday.at("17:00").do(self.generate_next_week_evaluation)
        
        # Schedule auto-submission for overdue evaluations every 10 minutes (strict)
        schedule.every(10).minutes.do(self.auto_submit_overdue_evaluations)
        
        # Schedule admin notifications every Sunday at 5:30 PM (30 minutes after evaluation starts)
        schedule.every().sunday.at("17:30").do(self.send_admin_evaluation_notification)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("✅ Scheduler started successfully")
        print("📅 Weekly evaluations will be auto-generated every Sunday at 5:00 PM")
        print("⏰ Overdue evaluations will be auto-submitted every 10 minutes (STRICT)")
        print("📧 Admin notifications will be sent every Sunday at 5:30 PM")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        print("🛑 Scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                time.sleep(60)
    
    def generate_next_week_evaluation(self):
        """Generate evaluation for next week - SUNDAY 5:00 PM"""
        try:
            print("🤖 Auto-generating next week's evaluation for SUNDAY 5:00 PM...")
            
            # Calculate next SUNDAY at 5:00 PM
            today = datetime.now()
            days_ahead = (6 - today.weekday() + 7) % 7  # Sunday is 6
            if days_ahead == 0:  # If today is Sunday, schedule for next Sunday
                days_ahead = 7
            
            next_sunday = (today + timedelta(days=days_ahead)).replace(
                hour=17, minute=0, second=0, microsecond=0  # 5:00 PM sharp
            )
            
            # Check if evaluation already exists
            existing = WeeklyEvaluation.query.filter(
                WeeklyEvaluation.scheduled_date.between(
                    next_sunday.replace(hour=0),
                    next_sunday.replace(hour=23, minute=59)
                )
            ).first()
            
            if existing:
                print(f"📅 Evaluation already exists for {next_sunday.strftime('%Y-%m-%d at %I:%M %p')}")
                return
            
            # Create evaluation with strict 60-minute duration
            custom_config = {
                'total_questions': 10,
                'coding_questions_count': 3,
                'mcq_questions_count': 7,
                'duration_minutes': 60  # STRICT 60 minutes
            }
            result = weekly_evaluation_service.create_weekly_evaluation(
                scheduled_date=next_sunday,
                custom_config=custom_config
            )
            
            if result['success']:
                print(f"✅ Auto-generated SUNDAY 5:00 PM evaluation for {next_sunday.strftime('%Y-%m-%d at %I:%M %p')}")
                print(f"📝 Evaluation ID: {result['evaluation_id']}")
                print(f"❓ Questions created: {result['questions_created']}")
                print(f"⏱️ Duration: 60 minutes STRICT (5:00 PM - 6:00 PM)")
            else:
                print(f"❌ Failed to auto-generate evaluation: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error in auto-generation: {e}")
    
    def auto_submit_overdue_evaluations(self):
        """Auto-submit evaluations that are overdue (STRICT 60 minutes after start)"""
        try:
            from models import WeeklyEvaluationAttempt
            
            # Find attempts that are overdue (more than 60 minutes past start time)
            cutoff_time = datetime.utcnow() - timedelta(minutes=60)  # STRICT 60 minutes
            
            overdue_attempts = db.session.query(WeeklyEvaluationAttempt).filter(
                WeeklyEvaluationAttempt.status == 'in_progress',
                WeeklyEvaluationAttempt.started_at < cutoff_time  # 60 minutes from start time
            ).all()
            
            if not overdue_attempts:
                return  # No overdue attempts
            
            print(f"⏰ Found {len(overdue_attempts)} overdue evaluation attempts (60+ minutes)")
            
            auto_submitted = 0
            for attempt in overdue_attempts:
                try:
                    # Auto-complete the evaluation with STRICT time enforcement
                    result = weekly_evaluation_service.complete_evaluation(str(attempt.id))
                    
                    if result['success']:
                        # Update status to auto_submitted with time penalty
                        attempt.status = 'auto_submitted'
                        # Apply time penalty - reduce score by 10% for late submission
                        if attempt.score_percentage:
                            attempt.score_percentage = max(0, attempt.score_percentage * 0.9)
                        db.session.commit()
                        auto_submitted += 1
                        
                        print(f"✅ Auto-submitted evaluation for user {attempt.user.name} (with 10% time penalty)")
                    else:
                        print(f"❌ Failed to auto-submit for user {attempt.user.name}: {result.get('error')}")
                        
                except Exception as e:
                    print(f"❌ Error auto-submitting attempt {attempt.id}: {e}")
                    db.session.rollback()
            
            if auto_submitted > 0:
                print(f"📝 Auto-submitted {auto_submitted} overdue evaluations with time penalties")
                # Send admin notification about auto-submissions
                self.send_admin_auto_submission_notification(auto_submitted)
                
        except Exception as e:
            print(f"❌ Error in auto-submission: {e}")
    
    def send_admin_evaluation_notification(self):
        """Send admin notification about active evaluation"""
        try:
            from email_service import email_service
            from models import WeeklyEvaluation
            
            # Find today's evaluation
            today = datetime.now()
            today_evaluation = WeeklyEvaluation.query.filter(
                WeeklyEvaluation.scheduled_date.between(
                    today.replace(hour=17, minute=0, second=0),
                    today.replace(hour=18, minute=0, second=0)
                ),
                WeeklyEvaluation.is_active == True
            ).first()
            
            if today_evaluation:
                subject = "📊 Weekly Evaluation Started - Admin Notification"
                html_body = f"""
                <h2>Weekly Evaluation Started</h2>
                <p><strong>Evaluation:</strong> {today_evaluation.title}</p>
                <p><strong>Started:</strong> {today_evaluation.scheduled_date.strftime('%Y-%m-%d at %I:%M %p')}</p>
                <p><strong>Duration:</strong> 60 minutes</p>
                <p><strong>Questions:</strong> {today_evaluation.total_questions}</p>
                <p><strong>Status:</strong> Active</p>
                <p>Students have 60 minutes to complete the evaluation. Auto-submission will occur after the time limit.</p>
                """
                
                email_service.send_email(
                    email_service.admin_email,
                    subject,
                    html_body,
                    f"Weekly Evaluation Started: {today_evaluation.title}"
                )
                print(f"📧 Admin notification sent for evaluation: {today_evaluation.title}")
                
        except Exception as e:
            print(f"❌ Error sending admin notification: {e}")
    
    def send_admin_auto_submission_notification(self, count):
        """Send admin notification about auto-submissions"""
        try:
            from email_service import email_service
            
            if count > 0:
                subject = f"⏰ Auto-Submitted {count} Overdue Evaluations"
                html_body = f"""
                <h2>Auto-Submission Report</h2>
                <p><strong>Auto-submitted evaluations:</strong> {count}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d at %I:%M %p')}</p>
                <p><strong>Reason:</strong> 60-minute time limit exceeded</p>
                <p><strong>Penalty Applied:</strong> 10% score reduction</p>
                <p>Please review the submissions in the admin portal.</p>
                """
                
                email_service.send_email(
                    email_service.admin_email,
                    subject,
                    html_body,
                    f"Auto-submitted {count} overdue evaluations with time penalties"
                )
                print(f"📧 Admin notification sent about {count} auto-submissions")
                
        except Exception as e:
            print(f"❌ Error sending auto-submission notification: {e}")
    
    def generate_evaluations_for_next_weeks(self, weeks_count=4):
        """Manually generate evaluations for the next few weeks"""
        try:
            result = weekly_evaluation_service.auto_generate_weekly_evaluations(weeks_count)
            
            if result['success']:
                print(f"✅ Generated {len(result['created_evaluations'])} evaluations")
                for eval_info in result['created_evaluations']:
                    print(f"📅 {eval_info['date']} - ID: {eval_info['evaluation_id']}")
            else:
                print(f"❌ Failed to generate evaluations: {result.get('error')}")
                
            return result
            
        except Exception as e:
            print(f"❌ Error generating evaluations: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_scheduler_status(self):
        """Get current scheduler status"""
        return {
            'running': self.running,
            'next_jobs': [str(job) for job in schedule.jobs],
            'thread_alive': self.scheduler_thread.is_alive() if self.scheduler_thread else False
        }

# Global scheduler instance
scheduler_service = SchedulerService()

# Auto-start scheduler when module is imported
def auto_start_scheduler():
    """Auto-start scheduler if not already running"""
    try:
        if not scheduler_service.running:
            scheduler_service.start_scheduler()
    except Exception as e:
        print(f"❌ Failed to auto-start scheduler: {e}")

# Auto-start scheduler when module is imported
auto_start_scheduler()