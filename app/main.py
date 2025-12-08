from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.models import Assignment, Task
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/test_auth')
def test_auth():
    if current_user.is_authenticated:
        return f"Logged in as: {current_user.name} ({current_user.user_type})"
    else:
        return "Not logged in"

@main.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        flash('Please log in to access this page.')
        return redirect(url_for('auth.login'))

    # Check for overdue assignments and update status
    if current_user.user_type == 'student':
        overdue_assignments = Assignment.query.filter_by(
            student_id=current_user.id,
            status='pending'
        ).join(Assignment.task).filter(
            Assignment.task.has(datetime.utcnow() > Task.deadline)
        ).all()

        if overdue_assignments:
            for assignment in overdue_assignments:
                assignment.status = 'overdue'
            db.session.commit()
            flash(f'You have {len(overdue_assignments)} overdue assignment(s)!', 'warning')

    if current_user.user_type == 'teacher':
        # Render teacher dashboard directly to avoid redirect issues
        tasks = Task.query.filter_by(created_by=current_user.id).all()

        # Get all students and their task statistics
        from models.models import User
        students = User.query.filter_by(user_type='student').all()

        student_stats = []
        for student in students:
            assignments = Assignment.query.filter_by(student_id=student.id).all()
            # Filter out assignments with deleted tasks
            assignments = [a for a in assignments if a.task is not None]
            total_tasks = len(assignments)
            completed_tasks = len([a for a in assignments if a.status == 'completed'])
            in_progress_tasks = len([a for a in assignments if a.status == 'in_progress'])
            overdue_tasks = len([a for a in assignments if a.is_overdue])

            student_stats.append({
                'student': student,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            })

        return render_template('teacher_dashboard.html', tasks=tasks, student_stats=student_stats)
    elif current_user.user_type == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.user_type == 'student':
        # Render student dashboard directly to avoid redirect issues
        assignments = Assignment.query.filter_by(student_id=current_user.id).all()
        # Filter out assignments with deleted tasks
        assignments = [a for a in assignments if a.task is not None]
        # Sort by priority and deadline
        priority_order = {
            'urgent_important': 1,
            'important_not_urgent': 2,
            'urgent_not_important': 3,
            'high_priority': 4,
            'medium_priority': 5,
            'low_priority': 6,
            'long_term': 7,
            'group_task': 8,
            'optional': 9,
            'not_important_not_urgent': 10
        }
        assignments.sort(key=lambda x: (priority_order.get(x.task.priority, 99), x.task.deadline))
        return render_template('student_dashboard.html', assignments=assignments)
    else:
        flash('Invalid user type. Please contact administrator.')
        return redirect(url_for('main.index'))