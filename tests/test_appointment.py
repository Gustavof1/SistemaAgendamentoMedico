from app import create_app
from app.database import db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment

def test_create_appointment_without_conflict():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        p = Patient(first_name="Joana", last_name="Oliveira", phone="111", address="Rua B")
        d = Doctor(first_name="José", last_name="Lima", email="doutorjoselima@email.com", specialty="Pediatra", clinic_address="Rua Clínica")
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
        p = Patient(first_name="Ana", last_name="Carvallho", phone="111", address="Rua B")
        d = Doctor(first_name="Paulo", last_name="Silva", email="doutorpaulosilva@email.com", specialty="Cardiologista", clinic_address="Rua Clínica")
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

def test_calendar_page():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        p = Patient(first_name="Joana", last_name="Oliveira", phone="111", address="Rua B")
        d = Doctor(first_name="José", last_name="Lima", email="doutorjoselima@email.com", specialty="Pediatra", clinic_address="Rua Clínica")
        db.session.add_all([p, d])
        db.session.commit()
        db.session.add(Appointment(patient_id=p.id, doctor_id=d.id, date="2025-06-01 10:00"))
        db.session.commit()
        resp = client.get("/calendar")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Joana Oliveira" in html
        assert "José Lima" in html
        assert "2025-06-01 10:00" in html

def test_create_appointment_dropdown():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        p = Patient(first_name="Ana", last_name="Carvallho", phone="111", address="Rua B")
        d = Doctor(first_name="Paulo", last_name="Silva", email="doutorpaulosilva@email.com", specialty="Cardiologista", clinic_address="Rua Clínica")
        db.session.add_all([p, d])
        db.session.commit()
        # Simula envio do formulário como seria pelo dropdown
        response = client.post("/form/appointment", data={
            "patient_id": str(p.id),
            "doctor_id": str(d.id),
            "date": "2025-07-01 09:00"
        }, follow_redirects=True)
        assert response.status_code == 200
        # Verifica se a consulta foi criada
        ap = db.session.query(Appointment).filter_by(patient_id=p.id, doctor_id=d.id, date="2025-07-01 09:00").first()
        assert ap is not None

def test_edit_appointment():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        p = Patient(first_name="Joana", last_name="Oliveira", phone="111", address="Rua B")
        d = Doctor(first_name="José", last_name="Lima", email="doutorjoselima@email.com", specialty="Pediatra", clinic_address="Rua Clínica")
        db.session.add_all([p, d])
        db.session.commit()
        ap = Appointment(patient_id=p.id, doctor_id=d.id, date="2025-06-01 10:00")
        db.session.add(ap)
        db.session.commit()
        # GET da página de edição
        resp = client.get(f"/edit/appointment/{ap.id}")
        assert resp.status_code == 200
        # POST para editar a data/hora
        response = client.post(f"/edit/appointment/{ap.id}", data={
            "date": "2025-06-01 11:00"
        }, follow_redirects=True)
        assert response.status_code == 200
        ap2 = db.session.get(Appointment, ap.id)
        assert ap2.date == "2025-06-01 11:00"

def test_create_appointment_conflict_warning():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        p = Patient(first_name="Ana", last_name="Carvallho", phone="111", address="Rua B")
        d = Doctor(first_name="Paulo", last_name="Silva", email="doutorpaulosilva@email.com", specialty="Cardiologista", clinic_address="Rua Clínica")
        db.session.add_all([p, d])
        db.session.commit()
        # Primeira consulta
        client.post("/form/appointment", data={
            "patient_id": str(p.id),
            "doctor_id": str(d.id),
            "date": "2025-07-01T09:00",
            "recurrence": "once"
        }, follow_redirects=True)
        # Segunda consulta em conflito (mesmo horário)
        resp = client.post("/form/appointment", data={
            "patient_id": str(p.id),
            "doctor_id": str(d.id),
            "date": "2025-07-01T09:15",
            "recurrence": "once"
        }, follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Atenção: Existe conflito de horário" in html

def test_create_appointment_recurrence():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        p = Patient(first_name="Ana", last_name="Carvallho", phone="111", address="Rua B")
        d = Doctor(first_name="Paulo", last_name="Silva", email="doutorpaulosilva@email.com", specialty="Cardiologista", clinic_address="Rua Clínica")
        db.session.add_all([p, d])
        db.session.commit()
        resp = client.post("/form/appointment", data={
            "patient_id": str(p.id),
            "doctor_id": str(d.id),
            "date": "2025-07-01T09:00",
            "recurrence": "15"
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Deve criar 5 consultas com intervalo de 15 dias
        from app.models.appointment import Appointment
        all_appointments = db.session.query(Appointment).filter_by(patient_id=p.id, doctor_id=d.id).all()
        assert len(all_appointments) == 5

def test_cancel_appointment():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        p = Patient(first_name="Joana", last_name="Oliveira", phone="111", address="Rua B")
        d = Doctor(first_name="José", last_name="Lima", clinic_address="Rua Clínica", specialty="Cardiologia", email="jose@medico.com")
        db.session.add_all([p, d])
        db.session.commit()
        ap = Appointment(patient_id=p.id, doctor_id=d.id, date="2025-06-01 10:00")
        db.session.add(ap)
        db.session.commit()
        resp = client.delete(f"/appointments/{ap.id}")
        assert resp.status_code == 200
        assert b"Consulta cancelada" in resp.data
        # Verifica se foi removido
        assert db.session.get(Appointment, ap.id) is None

def test_cancel_nonexistent_appointment():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        resp = client.delete("/appointments/9999")
        assert resp.status_code == 404
        assert b"Consulta nao encontrada" in resp.data

def test_create_doctor_missing_fields():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Faltando specialty e email
        resp = client.post("/doctors/", json={
            "first_name": "João",
            "last_name": "Souza",
            "clinic_address": "Av. Central, 456"
        })
        assert resp.status_code == 400
        assert b"Campo obrigatorio ausente" in resp.data

def test_create_patient_missing_fields():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Faltando campos obrigatórios
        resp = client.post("/patients/", json={
            "first_name": "",
            "last_name": "",
            "phone": "",
            "address": "",
            "email": ""
        })
        assert resp.status_code == 400
        assert b"Campo obrigatorio ausente" in resp.data
