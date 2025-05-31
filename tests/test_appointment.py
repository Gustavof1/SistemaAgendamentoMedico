from app import create_app
from app.database import db
from app.models.patient import Patient
from app.models.doctor import Doctor

def test_create_appointment_without_conflict():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        p = Patient(name="Joana")
        d = Doctor(name="Dr. José")
        db.session.add_all([p, d])
        db.session.commit()
        response = client.post("/appointments/", json={
            "patient_id": p.id,
            "doctor_id": d.id,
            "date": "2025-06-01 10:00"
        })
        assert response.status_code == 201

def test_create_appointment_with_conflict():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        p = Patient(name="Ana")
        d = Doctor(name="Dr. Paulo")
        db.session.add_all([p, d])
        db.session.commit()
        client.post("/appointments/", json={
            "patient_id": p.id,
            "doctor_id": d.id,
            "date": "2025-06-01 10:00"
        })
        response = client.post("/appointments/", json={
            "patient_id": p.id,
            "doctor_id": d.id,
            "date": "2025-06-01 10:00"
        })
        assert response.status_code == 409
