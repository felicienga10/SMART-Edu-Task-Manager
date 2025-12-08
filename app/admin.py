from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db
from models.models import User, Task, Assignment, Submission, Notification, Class, Subject
from .forms import AdminUserForm, SystemConfigForm, BulkOperationForm, ClassForm, SubjectForm
from werkzeug.security import generate_password_hash
import csv

admin = Blueprint('admin', __name__)

@admin.before_request
def require_admin():
    if not current_user.is_authenticated or current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('main.index'))

@admin.route('/')
@admin.route('/dashboard')
@login_required
def dashboard():
    # System statistics
    stats = {
        'total_users': User.query.count(),
        'total_teachers': User.query.filter_by(user_type='teacher').count(),
        'total_students': User.query.filter_by(user_type='student').count(),
        'total_classes': Class.query.count(),
        'total_tasks': Task.query.count(),
        'total_assignments': Assignment.query.count(),
        'total_submissions': Submission.query.count(),
        'completed_assignments': Assignment.query.filter_by(status='completed').count(),
        'overdue_tasks': Task.query.filter(Task.deadline < datetime.utcnow()).count()
    }
    
    # Recent activity
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    recent_tasks = Task.query.order_by(desc(Task.created_at)).limit(5).all()
    recent_submissions = Submission.query.order_by(desc(Submission.submitted_at)).limit(5).all()
    
    # Weekly activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_stats = {
        'new_users': User.query.filter(User.created_at >= week_ago).count(),
        'new_tasks': Task.query.filter(Task.created_at >= week_ago).count(),
        'new_submissions': Submission.query.filter(Submission.submitted_at >= week_ago).count()
    }
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         recent_tasks=recent_tasks,
                         recent_submissions=recent_submissions,
                         weekly_stats=weekly_stats)

@admin.route('/users')
@login_required
def manage_users():
    users = User.query.order_by(desc(User.created_at)).all()
    return render_template('admin_users.html', users=users)

@admin.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    form.class_id.choices = [(c.id, c.name) for c in Class.query.all()]

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.user_type = form.user_type.data
        user.subject = form.subject.data
        user.class_id = form.class_id.data

        if form.new_password.data:
            user.set_password(form.new_password.data)

        db.session.commit()
        flash(f'User {user.name} updated successfully!')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin_edit_user.html', form=form, user=user)

@admin.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.')
        return redirect(url_for('admin.manage_users'))
    
    # Delete related data first
    # Delete submissions for assignments belonging to this user
    assignment_ids = [assignment.id for assignment in Assignment.query.filter_by(student_id=user.id).all()]
    if assignment_ids:
        Submission.query.filter(Submission.assignment_id.in_(assignment_ids)).delete(synchronize_session=False)
    
    Assignment.query.filter_by(student_id=user.id).delete()
    Task.query.filter_by(created_by=user.id).delete()
    Notification.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} and all related data deleted successfully!')
    return redirect(url_for('admin.manage_users'))

@admin.route('/user/create', methods=['GET', 'POST'])
@login_required
def create_user():
    form = AdminUserForm()
    form.class_id.choices = [(c.id, c.name) for c in Class.query.all()]

    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            user_type=form.user_type.data,
            subject=form.subject.data,
            class_id=form.class_id.data
        )
        user.set_password(form.new_password.data or 'default123')
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.name} created successfully!')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin_create_user.html', form=form)

@admin.route('/analytics')
@login_required
def analytics():
    # User analytics
    user_stats = db.session.query(
        User.user_type,
        func.count(User.id).label('count')
    ).group_by(User.user_type).all()
    
    # Task priority distribution
    priority_stats = db.session.query(
        Task.priority,
        func.count(Task.id).label('count')
    ).group_by(Task.priority).all()
    
    # Monthly user registrations (last 12 months)
    monthly_users = db.session.query(
        func.strftime('%Y-%m', User.created_at).label('month'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= datetime.utcnow() - timedelta(days=365)).group_by('month').all()
    
    # Assignment status distribution
    assignment_stats = db.session.query(
        Assignment.status,
        func.count(Assignment.id).label('count')
    ).group_by(Assignment.status).all()
    
    return render_template('admin_analytics.html',
                         user_stats=user_stats,
                         priority_stats=priority_stats,
                         monthly_users=monthly_users,
                         assignment_stats=assignment_stats)

@admin.route('/tasks')
@login_required
def manage_tasks():
    tasks = Task.query.join(User).add_entity(User).order_by(desc(Task.created_at)).all()
    return render_template('admin_tasks.html', tasks=tasks)

@admin.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Delete related data
    # Delete submissions for assignments belonging to this task
    assignment_ids = [assignment.id for assignment in Assignment.query.filter_by(task_id=task.id).all()]
    if assignment_ids:
        Submission.query.filter(Submission.assignment_id.in_(assignment_ids)).delete(synchronize_session=False)
    
    Assignment.query.filter_by(task_id=task.id).delete()
    
    db.session.delete(task)
    db.session.commit()
    flash(f'Task "{task.title}" and all related data deleted successfully!')
    return redirect(url_for('admin.manage_tasks'))

@admin.route('/notifications/create', methods=['GET', 'POST'])
@login_required
def create_notification():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        notification_type = request.form.get('notification_type', 'info')
        target_users = request.form.get('target_users', 'all')
        
        # Create system notification
        Notification.create_system_notification(
            title=title,
            message=message,
            notification_type=notification_type,
            target_users=target_users,
            expires_in_hours=168  # 1 week
        )
        
        flash('System notification sent successfully!')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin_create_notification.html')

@admin.route('/export/users')
@login_required
def export_users():
    """Export user data to CSV"""
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'User Type', 'Subject/Class', 'Created At'])
    
    users = User.query.all()
    for user in users:
        writer.writerow([
            user.id,
            user.name,
            user.email,
            user.user_type,
            user.subject or user.class_name or '',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=users_export.csv'}
    )

@admin.route('/classes')
@login_required
def manage_classes():
    classes = Class.query.order_by(desc(Class.created_at)).all()
    return render_template('admin_classes.html', classes=classes)

@admin.route('/subjects')
@login_required
def manage_subjects():
    subjects = Subject.query.order_by(desc(Subject.created_at)).all()
    return render_template('admin_subjects.html', subjects=subjects)

@admin.route('/subject/create', methods=['GET', 'POST'])
@login_required
def create_subject():
    form = SubjectForm()
    form.class_id.choices = [(c.id, c.name) for c in Class.query.all()]

    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(subject)

        # Assign subject to the selected class
        selected_class = Class.query.get(form.class_id.data)
        if selected_class:
            subject.classes.append(selected_class)

        db.session.commit()
        flash(f'Subject "{subject.name}" created and assigned to class "{selected_class.name}" successfully!')
        return redirect(url_for('admin.manage_subjects'))

    return render_template('admin_create_subject.html', form=form)

@admin.route('/subject/<int:subject_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)
    form.class_id.choices = [(c.id, c.name) for c in Class.query.all()]

    # Pre-select current class
    if request.method == 'GET' and subject.classes:
        form.class_id.data = subject.classes[0].id

    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data

        # Update class assignment
        subject.classes = []
        selected_class = Class.query.get(form.class_id.data)
        if selected_class:
            subject.classes.append(selected_class)

        db.session.commit()
        flash(f'Subject "{subject.name}" updated successfully!')
        return redirect(url_for('admin.manage_subjects'))

    return render_template('admin_edit_subject.html', form=form, subject=subject)

@admin.route('/subject/<int:subject_id>/delete', methods=['POST'])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    # Check if subject is assigned to any classes
    if subject.classes:
        flash('Cannot delete subject that is assigned to classes.')
        return redirect(url_for('admin.manage_subjects'))

    db.session.delete(subject)
    db.session.commit()
    flash(f'Subject "{subject.name}" deleted successfully!')
    return redirect(url_for('admin.manage_subjects'))

@admin.route('/class/create', methods=['GET', 'POST'])
@login_required
def create_class():
    form = ClassForm()

    if form.validate_on_submit():
        class_obj = Class(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(class_obj)
        db.session.commit()

        flash(f'Class "{class_obj.name}" created successfully!')
        return redirect(url_for('admin.manage_classes'))

    return render_template('admin_create_class.html', form=form)

@admin.route('/class/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    form = ClassForm(obj=class_obj)

    if form.validate_on_submit():
        class_obj.name = form.name.data
        class_obj.description = form.description.data
        db.session.commit()
        flash(f'Class "{class_obj.name}" updated successfully!')
        return redirect(url_for('admin.manage_classes'))

    return render_template('admin_edit_class.html', form=form, class_obj=class_obj)

@admin.route('/class/<int:class_id>/delete', methods=['POST'])
@login_required
def delete_class(class_id):
    class_obj = Class.query.get_or_404(class_id)

    # Check if class has students or teachers assigned
    if class_obj.students or class_obj.teachers:
        flash('Cannot delete class that has students or teachers assigned.')
        return redirect(url_for('admin.manage_classes'))

    db.session.delete(class_obj)
    db.session.commit()
    flash(f'Class "{class_obj.name}" deleted successfully!')
    return redirect(url_for('admin.manage_classes'))

@admin.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for dashboard statistics"""
    stats = {
        'total_users': User.query.count(),
        'total_teachers': User.query.filter_by(user_type='teacher').count(),
        'total_students': User.query.filter_by(user_type='student').count(),
        'total_classes': Class.query.count(),
        'total_tasks': Task.query.count(),
        'completed_assignments': Assignment.query.filter_by(status='completed').count()
    }
    return jsonify(stats)