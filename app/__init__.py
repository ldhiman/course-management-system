from flask import Flask
from flask_sqlalchemy import SQLAlchemy


from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)

    # Check if we're in development mode before creating all tables
    if app.config['DEBUG']:
        with app.app_context():
            from app.models.Faculty import Faculty
            from app.models.Student import Student
            from app.models.Course import Course
            from app.models.Login import Login
            from app.models.Grade import Grade
            db.create_all()  # Create all database tables
            print("DB init..")

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    from app.faculty import bp as faculty_bp
    app.register_blueprint(faculty_bp, url_prefix='/faculty')

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'

    return app