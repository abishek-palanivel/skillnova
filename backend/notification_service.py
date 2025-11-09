from flask import current_app
from models import db, Notification, User
from datetime import datetime
import json

class NotificationService:
    @staticmethod
    def create_notification(user_id, notification_type, title, message, data=None):
        """Create a new notification for a user"""
        try:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                data=data
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return {
                'success': True,
                'notification_id': str(notification.id),
                'notification': {
                    'id': str(notification.id),
                    'type': notification.type,
                    'title': notification.title,
                    'message': notification.message,
                    'data': notification.data,
                    'created_at': notification.created_at.isoformat()
                }
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Failed to create notification: {str(e)}'
            }
    
    @staticmethod
    def create_video_call_notification(user_id, caller_name, call_id, room_id):
        """Create a video call notification"""
        title = f"Incoming Video Call"
        message = f"{caller_name} is calling you"
        data = {
            'call_id': call_id,
            'room_id': room_id,
            'caller_name': caller_name,
            'type': 'incoming_call'
        }
        
        return NotificationService.create_notification(
            user_id=user_id,
            notification_type='video_call',
            title=title,
            message=message,
            data=data
        )
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=False):
        """Get notifications for a user"""
        try:
            query = Notification.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(is_read=False)
            
            notifications = query.order_by(Notification.created_at.desc()).all()
            
            notifications_data = []
            for notification in notifications:
                notifications_data.append({
                    'id': str(notification.id),
                    'type': notification.type,
                    'title': notification.title,
                    'message': notification.message,
                    'data': notification.data,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat()
                })
            
            return {
                'success': True,
                'notifications': notifications_data
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get notifications: {str(e)}'
            }
    
    @staticmethod
    def mark_notification_read(notification_id, user_id):
        """Mark a notification as read"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification:
                return {
                    'success': False,
                    'message': 'Notification not found'
                }
            
            notification.is_read = True
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Notification marked as read'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Failed to mark notification as read: {str(e)}'
            }
    
    @staticmethod
    def delete_notification(notification_id, user_id):
        """Delete a notification"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification:
                return {
                    'success': False,
                    'message': 'Notification not found'
                }
            
            db.session.delete(notification)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Notification deleted'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Failed to delete notification: {str(e)}'
            }

# Create global instance
notification_service = NotificationService()