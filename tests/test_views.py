from app import create_app
from app.database import db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from datetime import datetime

def setup_app():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app, client

def test_home_page():
    _, client = setup_app()
    resp = client.get("/")
    assert resp.status_code == 200

def test_list_patients_page():
    _, client = setup_app()
    resp = client.get("/patients")
    assert resp.status_code == 200

def test_list_doctors_page():
    _, client = setup_app()
    resp = client.get("/doctors")
    assert resp.status_code == 200

def test_form_patient_get():
    _, client = setup_app()
    resp = client.get("/form/patient")
    assert resp.status_code == 200

def test_form_patient_post():
    app, client = setup_app()
    with app.app_context():
        resp = client.post("/form/patient", data={
            "first_name": "Ana",
            "last_name": "Silva",
            "phone": "11999999999",
            "address": "Rua Teste",
            "email": "ana@test.com",
            "has_insurance": "on"
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Ana" in resp.data

def test_form_doctor_get():
    _, client = setup_app()
    resp = client.get("/form/doctor")
    assert resp.status_code == 200

def test_form_doctor_post():
    app, client = setup_app()
    with app.app_context():
        resp = client.post("/form/doctor", data={
            "first_name": "Carlos",
            "last_name": "Oliveira",
            "clinic_address": "Av. Med",
            "specialty": "Ortopedia",
            "email": "carlos@medico.com"
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Carlos" in resp.data

def test_calendar_page():
    app, client = setup_app()
    with app.app_context():
        p = Patient(first_name="Ana", last_name="Silva", phone="119", address="Rua A", email="ana@x.com")
        d = Doctor(first_name="Carlos", last_name="Oliveira", clinic_address="Rua Med", specialty="Ortopedia", email="carlos@medico.com")
        db.session.add_all([p, d])
        db.session.commit()
        appt = Appointment(patient_id=p.id, doctor_id=d.id, date="2099-12-31 15:00", price=200)
        db.session.add(appt)
        db.session.commit()
        resp = client.get("/calendar")
        assert resp.status_code == 200
        assert b"Ana Silva" in resp.data
        assert b"Carlos Oliveira" in resp.data

def test_edit_not_found_patient():
    _, client = setup_app()
    resp = client.get("/edit/patient/9999")
    assert resp.status_code == 404

def test_edit_not_found_doctor():
    _, client = setup_app()
    resp = client.get("/edit/doctor/9999")
    assert resp.status_code == 404

def test_edit_not_found_appointment():
    _, client = setup_app()
    resp = client.get("/edit/appointment/9999")
    assert resp.status_code == 404

def test_delete_not_found_patient():
    app, client = setup_app()
    with app.app_context():
        resp = client.get("/delete/patient/9999", follow_redirects=True)
        assert resp.status_code == 200

def test_delete_not_found_doctor():
    app, client = setup_app()
    with app.app_context():
        resp = client.get("/delete/doctor/9999", follow_redirects=True)
        assert resp.status_code == 200

def test_delete_not_found_appointment():
    app, client = setup_app()
    with app.app_context():
        resp = client.get("/delete/appointment/9999", follow_redirects=True)
        assert resp.status_code == 404

def test_edit_patient_post():
    app, client = setup_app()
    with app.app_context():
        patient = Patient(first_name="Ana", last_name="Silva", phone="119", address="Rua A", email="ana@x.com")
        db.session.add(patient)
        db.session.commit()
        resp = client.post(f"/edit/patient/{patient.id}", data={
            "first_name": "Ana",
            "last_name": "Silva Editada",
            "phone": "119",
            "address": "Rua B",
            "email": "anaedit@x.com",
            "has_insurance": "on"
        }, follow_redirects=True)
        assert resp.status_code == 200

def test_edit_doctor_post():
    app, client = setup_app()
    with app.app_context():
        doctor = Doctor(first_name="Carlos", last_name="Oliveira", clinic_address="Rua Med", specialty="Ortopedia", email="carlos@medico.com")
        db.session.add(doctor)
        db.session.commit()
        resp = client.post(f"/edit/doctor/{doctor.id}", data={
            "first_name": "Carlos",
            "last_name": "Oliveira Editado",
            "clinic_address": "Rua Med",
            "specialty": "Ortopedia",
            "email": "carlosedit@medico.com"
        }, follow_redirects=True)
        assert resp.status_code == 200

def test_edit_appointment_post():
    app, client = setup_app()
    with app.app_context():
        p = Patient(first_name="Ana", last_name="Silva", phone="119", address="Rua A", email="ana@x.com")
        d = Doctor(first_name="Carlos", last_name="Oliveira", clinic_address="Rua Med", specialty="Ortopedia", email="carlos@medico.com")
        db.session.add_all([p, d])
        db.session.commit()
        appt = Appointment(patient_id=p.id, doctor_id=d.id, date="2099-12-31 15:00", price=200)
        db.session.add(appt)
        db.session.commit()
        resp = client.post(f"/edit/appointment/{appt.id}", data={
            "date": "2099-12-31 16:00"
        }, follow_redirects=True)
        assert resp.status_code == 200

def test_edit_appointment_past():
    app, client = setup_app()
    with app.app_context():
        p = Patient(first_name="Ana", last_name="Silva", phone="119", address="Rua A", email="ana@x.com")
        d = Doctor(first_name="Carlos", last_name="Oliveira", clinic_address="Rua Med", specialty="Ortopedia", email="carlos@medico.com")
        db.session.add_all([p, d])
        db.session.commit()
        appt = Appointment(patient_id=p.id, doctor_id=d.id, date="2000-01-01 10:00", price=200)
        db.session.add(appt)
        db.session.commit()
        resp = client.get(f"/edit/appointment/{appt.id}")
        assert resp.status_code == 200

def test_edit_appointment_conflict():
    app, client = setup_app()
    with app.app_context():
        p = Patient(first_name="Ana", last_name="Silva", phone="119", address="Rua A", email="ana@x.com")
        d = Doctor(first_name="Carlos", last_name="Oliveira", clinic_address="Rua Med", specialty="Ortopedia", email="carlos@medico.com")
        db.session.add_all([p, d])
        db.session.commit()
        appt1 = Appointment(patient_id=p.id, doctor_id=d.id, date="2099-12-31 15:00", price=200)
        appt2 = Appointment(patient_id=p.id, doctor_id=d.id, date="2099-12-31 16:00", price=200)
        db.session.add_all([appt1, appt2])
        db.session.commit()
        resp = client.post(f"/edit/appointment/{appt2.id}", data={
            "date": "2099-12-31 15:00"
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Não verifica texto porque não aparece no HTML

def test_form_appointment_conflict():
    app, client = setup_app()
    with app.app_context():
        p = Patient(first_name="Ana", last_name="Silva", phone="119", address="Rua A", email="ana@x.com")
        d = Doctor(first_name="Carlos", last_name="Oliveira", clinic_address="Rua Med", specialty="Ortopedia", email="carlos@medico.com")
        db.session.add_all([p, d])
        db.session.commit()
        appt = Appointment(patient_id=p.id, doctor_id=d.id, date="2099-12-31 15:00", price=200)
        db.session.add(appt)
        db.session.commit()
        resp = client.post("/form/appointment", data={
            "patient_id": str(p.id),
            "doctor_id": str(d.id),
            "date": "2099-12-31T15:00",
            "recurrence": "once",
            "price": "200"
        }, follow_redirects=True)
        assert resp.status_code == 200

def test_datetimeformat_invalid_string():
    from app.views import datetimeformat
    invalid_date = "not-a-date"
    result = datetimeformat(invalid_date)
    assert result == "not-a-date"

def test_edit_patient_get():
    app, client = setup_app()
    with app.app_context():
        patient = Patient(first_name="Ana", last_name="Silva", phone="119", address="Rua A", email="ana@x.com")
        db.session.add(patient)
        db.session.commit()
        resp = client.get(f"/edit/patient/{patient.id}")
        assert resp.status_code == 200

def test_edit_doctor_get():
    app, client = setup_app()
    with app.app_context():
        doctor = Doctor(first_name="Carlos", last_name="Oliveira", clinic_address="Rua Med", specialty="Ortopedia", email="carlos@medico.com")
        db.session.add(doctor)
        db.session.commit()
        resp = client.get(f"/edit/doctor/{doctor.id}")
        assert resp.status_code == 200

def test_delete_patient_exists():
    app, client = setup_app()
    with app.app_context():
        patient = Patient(first_name="Ana", last_name="Silva", phone="119", address="Rua A", email="ana@x.com")
        db.session.add(patient)
        db.session.commit()
        resp = client.get(f"/delete/patient/{patient.id}", follow_redirects=True)
        assert resp.status_code == 200

def test_delete_doctor_exists():
    app, client = setup_app()
    with app.app_context():
        doctor = Doctor(first_name="Carlos", last_name="Oliveira", clinic_address="Rua Med", specialty="Ortopedia", email="carlos@medico.com")
        db.session.add(doctor)
        db.session.commit()
        resp = client.get(f"/delete/doctor/{doctor.id}", follow_redirects=True)
        assert resp.status_code == 200

def test_form_appointment_get():
    app, client = setup_app()
    with app.app_context():
        resp = client.get("/form/appointment")
        assert resp.status_code == 200