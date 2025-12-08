# SMART Edu Task Manager - Project Structure

## Overview
This document provides a comprehensive overview of the SMART Edu Task Manager project structure, which is a Flask-based web application for task management between teachers and students with machine learning-powered priority classification.

## Features

### For Administrators
- System-wide user management (view, create, edit, delete users)
- Task management and oversight
- System analytics and reporting
- Notification system management
- Data export functionality
- System statistics and monitoring

### For Teachers
- Create tasks with detailed descriptions and deadlines
- Assign tasks to individual students or classes during creation
- Monitor student progress in real-time
- View comprehensive student performance overview
- Automatic priority suggestions using ML
- Review and manage student submissions

### For Students
- View assigned tasks sorted by priority and deadline
- Update task status (start, submit)
- Submit work through the platform
- Focus on high-priority tasks
- Receive notifications about assignments and updates
- Access notification center for updates

### Notification System
- Real-time in-app notifications
- System-wide announcements from admins
- Notification center with read/unread status
- Task assignment notifications
- Deadline reminders

### Machine Learning Integration
- Automatic task priority classification based on description
- Uses scikit-learn for text analysis and prediction

```
SMART Edu Task Manager/
├── README.md                          # Project documentation and instructions
├── requirements.txt                   # Python dependencies
├── run.py                             # Application entry point
├── migrate_db.py                      # Database migration script
├── architecture_plan.md              # Project architecture documentation
├── PROJECT_STRUCTURE.md              # This file
├── SYSTEM_ARCHITECTURE.md            # System architecture documentation
├── DATABASE_DESIGN.md                # Database schema documentation
├── TASK_WORKFLOW.md                  # Task workflow documentation
├── ADDITIONAL_FEATURES.md            # Additional features documentation
├── test_url.py                       # Testing utility script
├── create_admin.py                   # Admin user creation script
├── create_notifications_table.py     # Notification system setup
├── cookies.txt                       # Session/cookies data
├── app/                              # Main application package
│   ├── __init__.py                   # Flask app factory
│   ├── auth.py                       # Authentication routes
│   ├── main.py                       # Core application routes
│   ├── student.py                    # Student-specific routes
│   ├── teacher.py                    # Teacher-specific routes
│   ├── admin.py                      # Admin-specific routes
│   ├── notifications.py              # Notification system
│   └── forms.py                      # WTForms definitions
├── models/                           # Database models
│   └── models.py                     # SQLAlchemy model definitions
├── ml/                               # Machine Learning components
│   └── priority_predictor.py         # ML priority classification
├── templates/                        # Jinja2 HTML templates
│   ├── base.html                     # Base template with navigation
│   ├── index.html                    # Landing page
│   ├── login.html                    # User login page
│   ├── register_student.html         # Student registration
│   ├── register_teacher.html         # Teacher registration
│   ├── student_dashboard.html        # Student dashboard
│   ├── teacher_dashboard.html        # Teacher dashboard
│   ├── admin_dashboard.html          # Admin dashboard
│   ├── admin_users.html              # Admin user management
│   ├── admin_create_user.html        # Admin user creation
│   ├── admin_edit_user.html          # Admin user editing
│   ├── admin_analytics.html          # Admin analytics
│   ├── admin_tasks.html              # Admin task management
│   ├── admin_create_notification.html # Admin notification creation
│   ├── notification_center.html      # Notification center
│   ├── create_task.html              # Task creation form
│   ├── assign_task.html              # Task assignment form
│   ├── view_task.html                # Task details view
│   ├── submit_task.html              # Task submission form
│   ├── view_submission.html          # Submission review
│   ├── task_progress.html            # Progress tracking
│   └── review_submissions.html       # Submission review dashboard
├── static/                           # Static assets
│   └── style.css                     # Custom CSS styles
├── instance/                         # Instance-specific data
│   └── smart_edu.db                  # SQLite database
└── uploads/                          # User-uploaded files
    ├── *.docx                        # Document submissions
    └── *.pdf                         # PDF submissions
```

## Directory Structure Details

### Root Level Files
- **`run.py`**: Main application entry point that creates and runs the Flask app
- **`requirements.txt`**: Lists all Python dependencies needed for the project
- **`README.md`**: Comprehensive project documentation and setup instructions
- **`architecture_plan.md`**: Technical architecture and design decisions
- **`migrate_db.py`**: Database migration utilities
- **`test_url.py`**: URL testing and connectivity verification
- **`cookies.txt`**: Session management data

### Application Core (`app/`)
The main application package containing all Flask routes and business logic:

- **`__init__.py`**: Flask application factory with configuration
- **`auth.py`**: User authentication and session management
- **`main.py`**: Core application routes and home page functionality
- **`student.py`**: Student-specific routes and dashboard
- **`teacher.py`**: Teacher-specific routes and management features
- **`forms.py`**: WTForms definitions for form validation

### Database Layer (`models/`)
- **`models.py`**: SQLAlchemy database models for Users, Tasks, Assignments, and Submissions

### Machine Learning (`ml/`)
- **`priority_predictor.py`**: scikit-learn-based task priority classification system

### Web Templates (`templates/`)
Jinja2 HTML templates for the user interface:

- **Base Templates**: `base.html` provides common layout and navigation
- **Authentication**: `login.html`, `register_student.html`, `register_teacher.html`
- **Dashboards**: `student_dashboard.html`, `teacher_dashboard.html`
- **Task Management**: `create_task.html`, `assign_task.html`, `view_task.html`
- **Submission System**: `submit_task.html`, `view_submission.html`
- **Progress Tracking**: `task_progress.html`

### Static Assets (`static/`)
- **`style.css`**: Custom CSS styling for the application interface

### Data Storage
- **`instance/`**: Contains SQLite database and other instance-specific data
- **`uploads/`**: User-uploaded files including assignments and submissions

## Key Technologies Used

- **Backend**: Flask 2.x (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for form validation and CSRF protection
- **Frontend**: HTML5, CSS3, Bootstrap 5 (responsive design)
- **Machine Learning**: scikit-learn for priority prediction and text analysis
- **File Handling**: Werkzeug for secure file uploads with type/size validation
- **Notifications**: Real-time in-app notification system
- **Admin System**: Comprehensive administrative controls

## Features by Directory

### Admin Features (`admin.py`, `admin_dashboard.html`)
- System-wide user management (view, create, edit, delete users)
- Task management and oversight
- System analytics and reporting
- Notification system management
- Data export functionality
- System statistics and monitoring

### Teacher Features (`teacher.py`, `teacher_dashboard.html`)
- Create and assign tasks to students
- Monitor student progress and submissions
- View comprehensive student performance data
- Automatic priority suggestions via ML
- Review and manage submissions

### Student Features (`student.py`, `student_dashboard.html`)
- View assigned tasks sorted by priority and deadline
- Update task status (not started, in progress, submitted)
- Submit work files through the platform
- Track personal progress and deadlines
- Receive notifications about assignments

### Authentication (`auth.py`, forms from `forms.py`)
- User registration (separate flows for teachers and students)
- Secure login/logout functionality
- Session management and user role handling
- Admin user creation and management

### Notification System (`notifications.py`, `notification_center.html`)
- In-app notification center
- Real-time notification updates
- Mark notifications as read/unread
- System-wide notifications for admins
- Notification preferences (planned)

### Machine Learning (`ml/priority_predictor.py`)
- Automatic task priority classification
- Text analysis of task descriptions
- Predictive modeling for task importance

## Database Schema
The application uses four main models:
- **User**: Teachers and students with role-based access
- **Task**: Task details with descriptions and deadlines
- **Assignment**: Links tasks to specific students
- **Submission**: Student work submissions with file uploads

## Development Workflow
1. Install dependencies: `pip install -r requirements.txt`
2. Run application: `python run.py`
3. Access at: http://localhost:5000
4. Development server runs with debug mode enabled