from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from app import db
from models.models import Assignment, Submission
from .forms import SubmissionForm
import os
from werkzeug.utils import secure_filename

student = Blueprint('student', __name__)

@student.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 'student':
        return redirect(url_for('main.dashboard'))
    
    assignments = Assignment.query.filter_by(student_id=current_user.id).all()
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

@student.route('/task/<int:assignment_id>')
@login_required
def view_task(assignment_id):
    if current_user.user_type != 'student':
        return redirect(url_for('main.dashboard'))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.student_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('student.dashboard'))
    
    return render_template('view_task.html', assignment=assignment)

@student.route('/start_task/<int:assignment_id>')
@login_required
def start_task(assignment_id):
    if current_user.user_type != 'student':
        return redirect(url_for('main.dashboard'))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.student_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('student.dashboard'))
    
    assignment.status = 'in_progress'
    db.session.commit()
    flash('Task started!')
    return redirect(url_for('student.view_task', assignment_id=assignment_id))

@student.route('/submit_task/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_task(assignment_id):
    if current_user.user_type != 'student':
        return redirect(url_for('main.dashboard'))

    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.student_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('student.dashboard'))

    form = SubmissionForm()
    if form.validate_on_submit():
        file_path = None
        if form.file.data:
            filename = secure_filename(form.file.data.filename)
            if filename:
                # Create unique filename
                import uuid
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                form.file.data.save(file_path)

        submission = Submission(
            assignment_id=assignment.id,
            content=form.content.data,
            file_path=file_path
        )
        db.session.add(submission)
        assignment.status = 'completed'
        assignment.submitted_at = submission.submitted_at
        db.session.commit()
        flash('Task submitted successfully!')
        return redirect(url_for('student.dashboard'))

    return render_template('submit_task.html', form=form, assignment=assignment)

@student.route('/download_student_task_file/<int:task_id>')
@login_required
def download_student_task_file(task_id):
    print(f"DEBUG: Student download request for task {task_id} by user {current_user.id} ({current_user.user_type})")

    if current_user.user_type != 'student':
        print(f"DEBUG: Wrong user type: {current_user.user_type}")
        return f"<h1>Error: Access denied</h1><p>Students only (user type: {current_user.user_type})</p>", 403

    from models.models import Task
    task = Task.query.get_or_404(task_id)
    print(f"DEBUG: Task found: {task.title}, file_path: {task.file_path}")

    # Check if student is assigned to this task
    assignment = Assignment.query.filter_by(task_id=task_id, student_id=current_user.id).first()
    print(f"DEBUG: Assignment check: {assignment}")
    if not assignment:
        print(f"DEBUG: No assignment found for student {current_user.id} and task {task_id}")
        return f"<h1>Error: Access denied</h1><p>You are not assigned to task {task_id} (student_id: {current_user.id})</p>", 403

    if not task.file_path:
        print(f"DEBUG: No file path for task {task_id}")
        return f"<h1>Error: No file attached</h1><p>Task {task_id} has no attached file</p>", 404

    if not os.path.exists(task.file_path):
        print(f"DEBUG: File does not exist at {task.file_path}")
        return f"<h1>Error: File not found</h1><p>File not found at path: {task.file_path}</p>", 404

    print(f"DEBUG: Sending file: {task.file_path}")
    return send_file(task.file_path, as_attachment=True)