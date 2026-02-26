"""
Cleanup script for stuck video calls
Run this if you have calls stuck in 'waiting' or 'active' status
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, VideoCall
from app import create_app

def cleanup_stuck_calls():
    """Clean up video calls that are stuck in waiting/active status"""
    app = create_app()
    
    with app.app_context():
        # Find calls that have been waiting for more than 5 minutes
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        
        stuck_waiting_calls = VideoCall.query.filter(
            VideoCall.status == 'waiting',
            VideoCall.created_at < five_minutes_ago
        ).all()
        
        # Find calls that have been active for more than 2 hours (likely stuck)
        two_hours_ago = datetime.utcnow() - timedelta(hours=2)
        
        stuck_active_calls = VideoCall.query.filter(
            VideoCall.status == 'active',
            VideoCall.started_at < two_hours_ago
        ).all()
        
        print(f"Found {len(stuck_waiting_calls)} stuck waiting calls")
        print(f"Found {len(stuck_active_calls)} stuck active calls")
        
        # Update stuck waiting calls to 'cancelled'
        for call in stuck_waiting_calls:
            print(f"Cancelling waiting call: {call.id} (created {call.created_at})")
            call.status = 'cancelled'
            call.ended_at = datetime.utcnow()
        
        # Update stuck active calls to 'ended'
        for call in stuck_active_calls:
            print(f"Ending stuck active call: {call.id} (started {call.started_at})")
            call.status = 'ended'
            call.ended_at = datetime.utcnow()
            
            # Calculate duration if possible
            if call.started_at:
                duration = datetime.utcnow() - call.started_at
                call.duration_minutes = int(duration.total_seconds() / 60)
        
        db.session.commit()
        
        total_cleaned = len(stuck_waiting_calls) + len(stuck_active_calls)
        print(f"\n✅ Cleaned up {total_cleaned} stuck calls")
        
        return total_cleaned

if __name__ == '__main__':
    try:
        cleanup_stuck_calls()
    except Exception as e:
        print(f"❌ Error cleaning up calls: {str(e)}")
        import traceback
        traceback.print_exc()
