from flask import render_template, session, redirect, url_for, request, flash
from app.student import bp
from app.models.Student import Student
from app.models.Login import Login
from app.models.Course import Course
from app.models.Grade import Grade
import random
from datetime import datetime
from app import db

@bp.route('/')
def index():
    if 'userId' not in session:
        return redirect(url_for('student.login'))  # Use url_for for redirect
    _student = Student.query.get(session['userId'])
    if not _student:
        return redirect(url_for('student.login'))  # Use url_for for redirect
    print(_student)
    _courses = Grade.query.filter_by(student_id=_student.sid)
    return render_template('student/index.html', student=_student, courses=_courses)

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        _login = Login.query.filter_by(username=username).first()  # Change here
        print(_login)
        # Here you should add your user authentication logic
        # For example, checking the username and password against a database
        if _login is not None and _login.check_password(password):  # Replace with actual check
            session['userId'] = _login.id # Store userId in session
            flash('Login successful!', 'success')
            return redirect(url_for('student.index'))  # Redirect to the index page after login
        else:
            flash('Invalid username or password. Please try again.', 'danger')        
    
    return render_template('student/login.html')

@bp.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session['userId'] = None # Store userId in session
        flash('Login successful!', 'success')

    return render_template('student/login.html')



@bp.route('/register_courses/', methods=['GET', 'POST'])
def register_courses():
    active_courses = Course.query.filter(Course.end_date > db.func.current_date()).all()

    if request.method == 'POST':
        selected_courses = request.form.getlist('courses')  # Get the list of selected course IDs
        user_id = session.get('userId')  # Get user ID from session
        
        # Retrieve the student object
        _student = Student.query.get(user_id)

        for course_id in selected_courses:

            existing_grade = Grade.query.filter_by(student_id=_student.sid, course_id=course_id).first()
            if existing_grade:
                flash(f'You are already registered for the course: {existing_grade.course.name}.', 'warning')
                continue  # Skip to the next course
            
            new_grade = Grade(student_id=_student.sid, course_id=course_id)
            db.session.add(new_grade)


        db.session.commit()
        flash('You have successfully registered for the selected courses!', 'success')
        return redirect(url_for('student.index'))  # Redirect to a page after registration


    return render_template('student/register_courses.html', courses=active_courses)