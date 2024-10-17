from app import db
from sqlalchemy import func

class Student(db.Model):
    __tablename__ = 'student'
    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    roll_no = db.Column(db.String(100), nullable=False)
    regulation = db.Column(db.Text)
    fid = db.Column(db.Integer, db.ForeignKey('faculty.fid'))

    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    # Many-to-many relationship with Course through the Grade model
    grades = db.relationship('Grade', backref='student_rel')  # Unique backref name

    def __repr__(self):
        return f'<Student(name={self.name}, roll_no={self.roll_no})>'