from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models.models import Notification
from app import db
from datetime import datetime, timedelta

notifications = Blueprint('notifications', __name__)

@notifications.route('/api/notifications')
@login_required
def get_notifications():
    """API endpoint to get user notifications"""
    limit = request.args.get('limit', 10, type=int)
    include_read = request.args.get('include_read', False, type=bool)
    
    query = Notification.query.filter_by(user_id=current_user.id)
    
    # Filter out expired notifications
    query = query.filter(
        (Notification.expires_at.is_(None)) | 
        (Notification.expires_at > datetime.utcnow())
    )
    
    if not include_read:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.notification_type,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
            'expires_at': n.expires_at.isoformat() if n.expires_at else None,
            'is_expired': n.is_expired()
        } for n in notifications]
    })

@notifications.route('/api/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    notification = Notification.query.filter_by(
        id=notification_id, 
        user_id=current_user.id
    ).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

@notifications.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read for current user"""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({
        'is_read': True
    })
    db.session.commit()
    
    return jsonify({'success': True})

@notifications.route('/notifications')
@login_required
def notification_center():
    """Notification center page"""
    # Get all notifications for current user
    notifications = Notification.query.filter_by(user_id=current_user.id).filter(
        (Notification.expires_at.is_(None)) | 
        (Notification.expires_at > datetime.utcnow())
    ).order_by(Notification.created_at.desc()).all()
    
    # Count unread notifications
    unread_count = Notification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).filter(
        (Notification.expires_at.is_(None)) | 
        (Notification.expires_at > datetime.utcnow())
    ).count()
    
    return render_template('notification_center.html', 
                         notifications=notifications, 
                         unread_count=unread_count)

@notifications.route('/api/notifications/create', methods=['POST'])
@login_required
def create_notification():
    """Create a new notification (for testing and system use)"""
    data = request.get_json()
    
    if not data or not all(key in data for key in ['title', 'message']):
        return jsonify({'error': 'Title and message are required'}), 400
    
    notification = Notification.create_notification(
        user_id=current_user.id,
        title=data['title'],
        message=data['message'],
        notification_type=data.get('type', 'info'),
        expires_in_hours=data.get('expires_in_hours')
    )
    
    return jsonify({
        'success': True,
        'notification_id': notification.id
    })

# Helper functions for common notification scenarios
def notify_task_assigned(student_id, task_title, teacher_name):
    """Notify student when task is assigned"""
    return Notification.create_notification(
        user_id=student_id,
        title="New Task Assigned",
        message=f"Task '{task_title}' has been assigned by {teacher_name}",
        notification_type='info',
        expires_in_hours=168  # 7 days
    )

def notify_deadline_reminder(student_id, task_title, hours_left):
    """Notify student about deadline reminder"""
    if hours_left <= 0:
        title = "Task Deadline Passed"
        message = f"The deadline for task '{task_title}' has passed. Please submit your work as soon as possible."
        notification_type = 'warning'
    else:
        title = "Task Deadline Reminder"
        if hours_left < 1:
            message = f"Task '{task_title}' is due in {int(hours_left * 60)} minutes!"
        else:
            message = f"Task '{task_title}' is due in {hours_left:.1f} hours!"
        notification_type = 'warning'
    
    return Notification.create_notification(
        user_id=student_id,
        title=title,
        message=message,
        notification_type=notification_type,
        expires_in_hours=24
    )

def notify_submission_received(teacher_id, student_name, task_title):
    """Notify teacher when student submits work"""
    return Notification.create_notification(
        user_id=teacher_id,
        title="New Submission",
        message=f"{student_name} has submitted work for '{task_title}'",
        notification_type='success',
        expires_in_hours=168  # 7 days
    )

def send_system_announcement(title, message, target_users='all'):
    """Send system-wide announcement"""
    return Notification.create_system_notification(
        title=title,
        message=message,
        notification_type='info',
        target_users=target_users,
        expires_in_hours=168  # 7 days
    )

def notify_task_updated(student_ids, task_title, teacher_name):
    """Notify students when task is updated"""
    notifications = []
    for student_id in student_ids:
        notification = Notification.create_notification(
            user_id=student_id,
            title="Task Updated",
            message=f"Task '{task_title}' has been updated by {teacher_name}",
            notification_type='info',
            expires_in_hours=72  # 3 days
        )
        notifications.append(notification)
    
    return notifications

def notify_feedback_received(student_id, task_title, score):
    """Notify student when teacher provides feedback"""
    score_text = f"score of {score}/100" if score is not None else "feedback"
    return Notification.create_notification(
        user_id=student_id,
        title="Feedback Received",
        message=f"Teacher has provided {score_text} for task '{task_title}'",
        notification_type='success',
        expires_in_hours=168  # 7 days
    )