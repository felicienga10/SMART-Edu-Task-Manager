# SMART Edu Task Manager

A web-based platform that simplifies task management between teachers and students with priority-based classification using machine learning.

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

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate venv: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python run.py`

## Usage

### Getting Started
1. Register as a teacher, student, or use admin credentials
2. Login to access your dashboard
3. Explore your role-specific features

### For Administrators
- Access admin dashboard at `/admin` (default admin: admin@smartedu.com / admin123)
- Manage users, tasks, and system settings
- Create system notifications
- View analytics and reports

### For Teachers
- Create tasks and assign them to students during creation
- Monitor student progress and submissions
- Review and manage student work

### For Students
- View and complete assigned tasks
- Update task status and submit work
- Receive notifications and updates

## Technology Stack

- Backend: Flask (Python)
- Database: SQLite with SQLAlchemy
- Frontend: HTML, CSS, Bootstrap
- ML: scikit-learn
- Authentication: Flask-Login

## Project Structure

```
smart-edu-task-manager/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── main.py
│   ├── teacher.py
│   ├── student.py
│   ├── admin.py
│   ├── notifications.py
│   └── forms.py
├── models/
│   └── models.py
├── ml/
│   └── priority_predictor.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── admin_users.html
│   ├── notification_center.html
│   └── ... (more templates)
├── static/
│   └── style.css
├── uploads/
├── create_admin.py
├── run.py
├── requirements.txt
├── ML_ALGORITHM.md                   # ML priority prediction algorithm docs
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

## License

This project is licensed under the MIT License.