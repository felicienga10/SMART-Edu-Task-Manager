from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Association table for teacher-class many-to-many relationship
teacher_classes = db.Table('teacher_classes',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True)
)

# Association table for class-subject many-to-many relationship
class_subjects = db.Table('class_subjects',
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

# Association table for teacher-subject selections (which subjects teacher teaches)
teacher_subjects = db.Table('teacher_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

# Association table for teacher-subject-class many-to-many relationship
teacher_class_subjects = db.Table('teacher_class_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    creator = db.relationship('User', backref='created_subjects', lazy=True, foreign_keys=[created_by])
    classes = db.relationship('Class', secondary=class_subjects, backref='subjects', lazy=True)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    creator = db.relationship('User', backref='created_classes', lazy=True, foreign_keys=[created_by])
    students = db.relationship('User', backref='student_class', lazy=True, foreign_keys='User.class_id')
    teachers = db.relationship('User', secondary=teacher_classes, backref='teaching_classes', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'teacher', 'student', or 'admin'
    subject = db.Column(db.String(100))  # for teachers
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))  # for students
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    created_tasks = db.relationship('Task', backref='creator', lazy=True)
    assignments = db.relationship('Assignment', backref='student', lazy=True)
    selected_subjects = db.relationship('Subject', secondary=teacher_subjects, backref='teaching_teachers', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(50), nullable=False)
    instructions = db.Column(db.Text)
    file_path = db.Column(db.String(500))  # Path to uploaded task file
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assignments = db.relationship('Assignment', backref='task', lazy=True)

    @property
    def is_overdue(self):
        from datetime import datetime
        return datetime.utcnow() > self.deadline

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, overdue
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)

    # Relationships
    submissions = db.relationship('Submission', backref='assignment', lazy=True)

    @property
    def is_overdue(self):
        from datetime import datetime
        # Handle case where task has been deleted
        if self.task is None:
            return False
        return datetime.utcnow() > self.task.deadline and self.status != 'completed'

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Feedback fields
    score = db.Column(db.Integer, nullable=True)  # Score/grade (0-100)
    feedback = db.Column(db.Text, nullable=True)  # Teacher feedback comments
    feedback_provided_at = db.Column(db.DateTime, nullable=True)  # When feedback was provided
    graded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Teacher who graded

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False, default='info')  # info, success, warning, error
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='notifications', lazy=True)
    
    def is_expired(self):
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @staticmethod
    def create_notification(user_id, title, message, notification_type='info', expires_in_hours=None):
        """Create a new notification for a user"""
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            expires_at=expires_at
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def create_system_notification(title, message, notification_type='info', target_users='all', expires_in_hours=24):
        """Create system notifications for multiple users"""
        from models.models import User
        
        if target_users == 'all':
            users = User.query.all()
        elif target_users == 'teachers':
            users = User.query.filter_by(user_type='teacher').all()
        elif target_users == 'students':
            users = User.query.filter_by(user_type='student').all()
        else:
            return []
        
        notifications = []
        for user in users:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            notification = Notification(
                user_id=user.id,
                title=title,
                message=message,
                notification_type=notification_type,
                expires_at=expires_at
            )
            db.session.add(notification)
            notifications.append(notification)
        
        db.session.commit()
        return notifications