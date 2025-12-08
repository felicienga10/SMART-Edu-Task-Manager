from app import create_app, db
from models.models import User, Task, Assignment, Submission

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Task': Task, 'Assignment': Assignment, 'Submission': Submission}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)