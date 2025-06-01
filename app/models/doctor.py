from ..database import db

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    clinic_address = db.Column(db.String(200))
    specialty = db.Column(db.String(100), nullable=False)  # novo campo obrigatório
    email = db.Column(db.String(120), nullable=False)      # novo campo obrigatório

    def total_earned(self):
        from .appointment import Appointment
        return sum([a.price or 0 for a in Appointment.query.filter_by(doctor_id=self.id).all()])
