from app import db

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    subject = db.Column(db.String(150), nullable=False)

    # Many-to-many relationship with Student through the Grade model
    grades = db.relationship('Grade', backref='course_rel')  # Unique backref name

    def __repr__(self):
        return f'<Course(name={self.name}, subject={self.subject})>'
