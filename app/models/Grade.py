from app import db

class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the grade
    student_id = db.Column(db.Integer, db.ForeignKey('student.sid'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    grade = db.Column(db.String(10))  # Field to store the grade (like 'A', 'B', 'C', etc.)

    student = db.relationship('Student', backref='student_grades')  # Use a unique backref name
    course = db.relationship('Course', backref='course_grades')  # Use a unique backref name


    def __repr__(self):
        return f'<Grade(student_id={self.student_id}, course_id={self.course_id}, grade={self.grade})>'