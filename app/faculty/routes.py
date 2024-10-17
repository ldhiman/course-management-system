
from flask import render_template, session, redirect, url_for, request, flash
from app.faculty import bp
from app.models.Student import Student
from app.models.Login import Login
from app.models.Course import Course
from app.models.Grade import Grade
from app.models.Faculty import Faculty
import random
from datetime import datetime
from app import db

@bp.route('/')
def index():
    if 'userId' not in session:
        return redirect(url_for('faculty.login'))  # Redirect if user is not logged in
    _faculty = Faculty.query.get(session['userId'])
    if not _faculty:
        return redirect(url_for('faculty.login'))  # Redirect if faculty not found

    _course = Course.query.get(_faculty.course_id)
    enrolled_students_list = Grade.query.filter_by(course_id=_faculty.course_id).all()  # Get all grades for the course

    # Create a dictionary to map student IDs to their grades for easy access
    # student_grades = {grade.student_id: grade for grade in enrolled_students_list}

    return render_template('faculty/index.html', faculty=_faculty, course=_course, enrolled_students=enrolled_students_list, student_grades=enrolled_students_list)


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
            return redirect(url_for('faculty.index'))  # Redirect to the index page after login
        else:
            flash('Invalid username or password. Please try again.', 'danger')        
    
    return render_template('faculty/login.html')

@bp.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session['userId'] = None # Store userId in session
        flash('Login successful!', 'success')
         
    return render_template('faculty/login.html')

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level
logger = logging.getLogger(__name__)  # Create a logger object

@bp.route('/submit_grade', methods=['POST'])
def submit_grade():
    student_id = request.form.get('student_id')  # Get student ID from form
    course_id = request.form.get('course_id')    # Get course ID from form
    grade = request.form.get('grade')            # Get the grade from the form
    
    # Log the submission attempt
    logger.info(f'Attempting to submit grade: {grade} for Student ID: {student_id}, Course ID: {course_id}')

    # Retrieve the grade record for the specified student and course
    student_grade = Grade.query.filter_by(student_id=student_id, course_id=course_id).first()

    if student_grade:
        # Update existing grade if found
        old_grade = student_grade.grade  # Store the old grade for logging
        student_grade.grade = grade
        logger.info(f'Updated grade for Student ID: {student_id} from {old_grade} to {grade}')
    else:
        # Create a new grade entry if one doesn't exist
        new_grade = Grade(student_id=student_id, course_id=course_id, grade=grade)
        db.session.add(new_grade)  # Add new grade record to the session
        logger.info(f'Created new grade entry for Student ID: {student_id}, Course ID: {course_id} with grade: {grade}')

    try:
        db.session.commit()  # Commit the changes to the database
        flash('Grade submitted successfully!', 'success')  # Flash success message
        logger.info('Grade submission committed to database successfully.')
    except Exception as e:
        db.session.rollback()  # Roll back the session on error
        logger.error(f'Error submitting grade for Student ID: {student_id}, Course ID: {course_id}. Error: {str(e)}')
        flash(f'An error occurred while submitting the grade: {str(e)}', 'danger')  # Flash error message

    return redirect(url_for('faculty.index'))  # Redirect back to the faculty index page
