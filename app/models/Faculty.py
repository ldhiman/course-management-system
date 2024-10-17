from app import db

class Faculty(db.Model):
    __tablename__ = 'faculty'  # Optional: Define a table name if not following default
    fid = db.Column(db.Integer, db.ForeignKey('login.id'), primary_key=True)  # Corrected ForeignKey
    name = db.Column(db.String(150), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))  # Corrected ForeignKey
    designation = db.Column(db.Text)
    subject = db.Column(db.Text)

    # Relationships
    course = db.relationship('Course', backref='faculty_members')  # Add relationship to Course

    def __repr__(self):
        return f'<Faculty(name={self.name}, designation={self.designation})>'
