from ..database import db

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    email = db.Column(db.String(120))  # novo campo
    has_insurance = db.Column(db.Boolean, default=False)  # novo campo
