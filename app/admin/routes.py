from flask import render_template, session, redirect, url_for, request, flash
from app.admin import bp
from app.models.Student import Student
from app.models.Login import Login
from app.models.Course import Course
from app.models.Faculty import Faculty
from app.models.Grade import Grade
import random
from datetime import datetime
from app import db
@bp.route('/')
def index():
    if 'userId' not in session:
        return redirect(url_for('admin.login'))  # Use url_for for redirect
    
    total_student = Student.query.count()
    total_faculty = Faculty.query.count()  # Use count() for better performance
    # Get the current date
    current_date = datetime.now().date()
    # Count only active courses that have not ended yet
    active_courses = Course.query.filter(Course.start_date <= current_date, Course.end_date >= current_date).count()

    return render_template('admin/index.html', list=[total_student, total_faculty, active_courses])


@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Here you should add your user authentication logic
        # For example, checking the username and password against a database
        if username == "admin" and password == "admin":  # Replace with actual check
            session['userId'] = "admin"  # Store userId in session
            flash('Login successful!', 'success')
            return redirect(url_for('admin.index'))  # Redirect to the index page after login
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('admin/login.html')


@bp.route('/create_student/', methods=["GET", "POST"])
def create_student():
    if request.method == "POST":
        roll_no = request.form.get("roll_no").upper()
        name = request.form.get("name")
        regulation = request.form.get("regulation")

        # Generate a random password and hash it
        password = str(random.randint(10000, 99999))  # Convert to string for hashing
        _login = Login(username=roll_no, role="Student")
        _login.set_password(password)  # Hash the password

        try:
            # Add the login to the session and commit
            db.session.add(_login)
            db.session.commit()  # Commit to get the ID for the login

            # Create the student record
            _student = Student(sid=_login.id, name=name, roll_no=roll_no, regulation=regulation)
            db.session.add(_student)
            db.session.commit()  # Commit to save the student
            
            # Optionally: Flash a message to the user
            flash(f'Student created successfully! Username: {roll_no}, Password: {password}', 'success')
            return redirect(url_for('admin.create_student'))  # Redirect to an appropriate page after success

        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash('An error occurred while creating the student.', 'danger')
            print(e)  # Optionally log the error

    return render_template('admin/create_student.html')

@bp.route('/manage_student', methods=['GET'])
def list_student():
    # Fetch all students and their related login info
    users = db.session.query(Student, Login).join(Login, Student.sid == Login.id).all()
    return render_template('admin/student_list.html', users=users)

@bp.route('/user/<int:sid>', methods=['GET'])
def user_detail(sid):
    # Fetch user details by sid
    student = Student.query.get(sid)
    if student is None:
        return redirect(url_for('admin.list_student'))  # Redirect if not found
    login_info = Login.query.get(sid)
    grades = Grade.query.filter_by(student_id=sid).all()
    return render_template('admin/student_detail.html', student=student, login_info=login_info, courses=grades)

@bp.route('/user/<int:sid>/update_password', methods=['POST'])
def update_password(sid):
    user = Login.query.get(sid)
    if user:
        new_password = request.form['new_password']
        user.set_password(new_password)  # Hash the new password
        db.session.commit()
        flash('Password updated successfully!', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('admin.user_detail', sid=sid))

@bp.route('/user/<int:sid>/delete', methods=['POST'])
def delete_student(sid):
    student = Student.query.get(sid)
    user = Login.query.get(sid)

    if student and user:
        # First, delete the student record
        db.session.delete(student)
        # Then, delete the related login record
        db.session.delete(user)
        # Commit both deletions
        db.session.commit()
        flash('Student and associated login deleted successfully!', 'success')
    else:
        flash('Student or login not found.', 'danger')

    return redirect(url_for('admin.list_student'))

@bp.route('/user/<int:id>/deregister_student/<int:sid>', methods=['POST'])
def deregister_student(id,sid):
    _grade = Grade.query.get(id)
    if _grade:
        db.session.delete(_grade)
        db.session.commit()
        flash('Deregistered successfully!', 'success')
    else:
        flash('Course Registeration not found.', 'danger')
    return redirect(url_for('admin.user_detail', sid=sid))
    


@bp.route('/update_user/<int:sid>', methods=['POST'])
def update_user(sid):
    student = Student.query.get(sid)
    if not student:
        flash("User not found.", "danger")
        return redirect(url_for('admin.list_student'))

    username = request.form['username']
    roll_no = request.form['roll_no']
    name = request.form['name']
    regulation = request.form['regulation']

    # Update fields
    login_info = Login.query.filter_by(id=sid).first()
    if login_info:
        login_info.username = username  # Update username in Login table

    student.roll_no = roll_no
    student.name = name
    student.regulation = regulation

    db.session.commit()
    flash("User details updated successfully.", "success")
    return redirect(url_for('admin.user_detail', sid=sid))

@bp.route('/create_faculty/', methods=["GET", "POST"])
def create_faculty():
    if request.method == "POST":
        designation = request.form.get("designation")
        subject = request.form.get("subject")
        name = request.form.get("name")
        course_id = request.form['course']  # Get selected course ID


        # Generate a random password and hash it
        username = name.split(" ")[0] + str(random.randint(100, 999))
        password = str(random.randint(10000, 99999))  # Convert to string for hashing
        _login = Login(username=username, role="Faculty")
        _login.set_password(password)  # Hash the password

        try:
            # Add the login to the session and commit
            db.session.add(_login)
            db.session.commit()  # Commit to get the ID for the login

            # Create the student record
            _faculty = Faculty(fid=_login.id, name=name, designation=designation, subject=subject)

            if course_id:
                course = Course.query.get(course_id)
                if course:
                    _faculty.course = course  # Assuming you have a relationship set up in Faculty

            db.session.add(_faculty)
            db.session.commit()  # Commit to save the student
            
            # Optionally: Flash a message to the user
            flash(f'Faculty created successfully! Username: {username}, Password: {password}', 'success')
            return redirect(url_for('admin.create_faculty'))  # Redirect to an appropriate page after success

        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            flash('An error occurred while creating the student.', 'danger')
            print(e)  # Optionally log the error
    
    _courses = Course.query.all()
    return render_template('admin/create_faculty.html', courses=_courses)

@bp.route('/manage_faculty', methods=['GET'])
def list_faculty():
    # Fetch all students and their related login info
    users = db.session.query(Faculty, Login).join(Login, Faculty.fid == Login.id).all()
    return render_template('admin/faculty_list.html', users=users)

@bp.route('/faculty/<int:fid>', methods=['GET'])
def faculty_detail(fid):
    # Fetch user details by sid
    faculty = Faculty.query.get(fid)
    if faculty is None:
        return redirect(url_for('admin.list_faculty'))  # Redirect if not found
    login_info = Login.query.get(faculty.fid)
    return render_template('admin/faculty_detail.html', faculty=faculty, login_info=login_info)

@bp.route('/faculty/<int:fid>/update_password', methods=['POST'])
def update_password_faculty(fid):
    user = Login.query.get(fid)
    if user:
        new_password = request.form['new_password']
        user.set_password(new_password)  # Hash the new password
        db.session.commit()
        flash('Password updated successfully!', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('admin.faculty_detail', fid=fid))

@bp.route('/update_faculty/<int:fid>', methods=['POST'])
def update_faculty(fid):
    faculty = Faculty.query.get(fid)
    if not faculty:
        flash("User not found.", "danger")
        return redirect(url_for('admin.list_faculty'))

    name = request.form['name']
    designation = request.form['designation']
    subject = request.form['subject']

    faculty.name = name
    faculty.designation = designation
    faculty.subject = subject

    db.session.commit()
    flash("User details updated successfully.", "success")
    return redirect(url_for('admin.faculty_detail', fid=fid))

@bp.route('/delete_faculty/<int:fid>', methods=['POST'])
def delete_faculty(fid):
    faculty = Faculty.query.get(fid)
    login = Login.query.get(fid)
    if faculty:
        db.session.delete(login)
        db.session.delete(faculty)
        db.session.commit()
        flash('Faculty member has been successfully deleted.', 'success')
    else:
        flash('Faculty member not found.', 'danger')
    return redirect(url_for('admin.list_faculty'))

@bp.route('/create_course/', methods=["GET", "POST"])
def create_course():
    if request.method == "POST":
        # Retrieve form data
        id = request.form.get("id")
        name = request.form.get("name")
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")
        subject = request.form.get("subject")

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()


            # Create a new course instance
            _course = Course(course_id=id, name=name, start_date=start_date, end_date=end_date, subject=subject)
            db.session.add(_course)  # Add the course to the session
            db.session.commit()  # Commit to save the course
            
            # Flash a success message to the user
            flash('Course created successfully!', 'success')
            return redirect(url_for('admin.list_courses'))  # Redirect to a page showing the list of courses

        except Exception as e:
            db.session.rollback()  # Rollback the session in case of error
            flash('An error occurred while creating the course. Please try again.', 'danger')
            print(e)  # Log the error for debugging purposes
            
    return render_template('admin/create_course.html')

@bp.route('/courses/')
def list_courses():
    courses = Course.query.all()  # Fetch all courses from the database
    return render_template('admin/list_courses.html', courses=courses)

@bp.route('/edit_course/<string:course_id>/', methods=['GET', 'POST'])
def edit_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        flash('Course not found!', 'danger')
        return redirect(url_for('admin.list_courses'))

    if request.method == 'POST':
        course.name = request.form.get('name')
        course.subject = request.form.get('subject')

        course.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        course.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()

        try:
            db.session.commit()
            flash('Course updated successfully!', 'success')
            return redirect(url_for('admin.list_courses'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the course.', 'danger')
            print(e)

    return render_template('admin/edit_course.html', course=course)

@bp.route('/delete_course/<string:course_id>/', methods=['POST'])
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        flash('Course not found!', 'danger')
        return redirect(url_for('admin.list_courses'))

    try:
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the course.', 'danger')
        print(e)

    return redirect(url_for('admin.list_courses'))

