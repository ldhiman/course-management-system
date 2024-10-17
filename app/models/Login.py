from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Login(db.Model):
    __tablename__ = 'login'  # Optional: Define a table name if not following default
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing is implied
    username = db.Column(db.String(150), nullable=False, unique=True)  # Unique usernames
    password = db.Column(db.String(128), nullable=False)  # Adjusted length for hashed passwords
    role = db.Column(db.String(128), nullable=False)  # Student, Faculty, Admin

    def __repr__(self):
        return f'<Login(username={self.username})>'

    def set_password(self, password):
        """Hash the password and set the password field."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hashed password."""
        return check_password_hash(self.password, password)
