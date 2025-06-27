import pytest
from app import create_app
from app.database import db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment

@pytest.fixture
def client():
    """Fixture que cria uma instância da aplicação e um banco de dados limpo para cada teste."""
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client

# --- TESTES DE INTEGRAÇÃO ---

def test_integration_insurance_discount_logic(client):
    """
    Verifica o fluxo de criação e a lógica de negócio do desconto de convênio.
    1. Cria um médico via API.
    2. Cria um paciente SEM convênio.
    3. Cria um paciente COM convênio.
    4. Agenda uma consulta para o paciente SEM convênio e verifica se o preço pago é integral.
    5. Agenda uma consulta para o paciente COM convênio e verifica se o preço pago é 50%.
    """
    # 1. Cria médico
    resp_doc = client.post("/doctors/", json={"first_name": "Dr. House", "last_name": "G", "email": "house@email.com", "specialty": "Diagnóstico", "clinic_address": "Rua A"})
    assert resp_doc.status_code == 201
    doc_id = resp_doc.get_json()["id"]

    # 2. Cria paciente SEM convênio
    resp_p1 = client.post("/patients/", json={"first_name": "Paciente", "last_name": "Sem Convênio", "phone": "1", "address": "Rua B", "email": "sem@convenio.com", "has_insurance": False})
    assert resp_p1.status_code == 201
    p1_id = resp_p1.get_json()["id"]
    
    # 3. Cria paciente COM convênio
    resp_p2 = client.post("/patients/", json={"first_name": "Paciente", "last_name": "Com Convênio", "phone": "2", "address": "Rua C", "email": "com@convenio.com", "has_insurance": True})
    assert resp_p2.status_code == 201
    p2_id = resp_p2.get_json()["id"]

    # 4. Agenda para paciente SEM convênio
    resp_app1 = client.post("/appointments/", json={"patient_id": p1_id, "doctor_id": doc_id, "date": "2025-08-01 14:00", "price": 300})
    assert resp_app1.status_code == 201
    # Verifica se o preço pago é o valor total (300)
    assert resp_app1.get_json()["price_paid"] == 300.0

    # 5. Agenda para paciente COM convênio
    resp_app2 = client.post("/appointments/", json={"patient_id": p2_id, "doctor_id": doc_id, "date": "2025-08-01 15:00", "price": 300})
    assert resp_app2.status_code == 201
    # Verifica se o preço pago é 50% do valor (150)
    assert resp_app2.get_json()["price_paid"] == 150.0

def test_integration_schedule_conflict_check(client):
    """
    Verifica a regra de negócio que impede agendamentos conflitantes.
    1. Cria um médico e um paciente.
    2. Agenda uma consulta para as 10:00 (deve ter sucesso).
    3. Tenta agendar outra consulta para o mesmo médico às 10:15 (deve falhar com conflito).
    4. Tenta agendar outra consulta para o mesmo médico às 10:30 (deve ter sucesso).
    """
    # 1. Cria entidades
    resp_doc = client.post("/doctors/", json={"first_name": "Dr. Plantão", "last_name": "S.", "email": "plantao@email.com", "specialty": "Emergência", "clinic_address": "Hospital"})
    doc_id = resp_doc.get_json()["id"]
    resp_pat = client.post("/patients/", json={"first_name": "Paciente", "last_name": "Urgente", "phone": "192", "address": "Rua Urgencia", "email": "urgente@email.com"})
    pat_id = resp_pat.get_json()["id"]

    # 2. Agenda às 10:00 (sucesso)
    resp1 = client.post("/appointments/", json={"patient_id": pat_id, "doctor_id": doc_id, "date": "2025-09-10 10:00", "price": 100})
    assert resp1.status_code == 201

    # 3. Agenda às 10:15 (conflito)
    resp2 = client.post("/appointments/", json={"patient_id": pat_id, "doctor_id": doc_id, "date": "2025-09-10 10:15", "price": 100})
    assert resp2.status_code == 409 # 409 Conflict
    assert "Doctor is already booked" in resp2.get_json()["error"]

    # 4. Agenda às 10:30 (sucesso)
    resp3 = client.post("/appointments/", json={"patient_id": pat_id, "doctor_id": doc_id, "date": "2025-09-10 10:30", "price": 100})
    assert resp3.status_code == 201

def test_integration_doctor_total_earned_calculation(client):
    """
    Verifica se o método total_earned() do médico calcula o saldo corretamente, considerando os valores efetivamente pagos (com desconto de convênio).
    1. Cria um médico e dois pacientes (um com convênio, outro sem).
    2. Agenda consultas para ambos.
    3. Busca o médico no banco de dados e chama o método total_earned().
    4. Verifica se a soma corresponde aos valores pagos.
    """
    # 1. Cria entidades
    app = client.application # Pega a instância da app para usar o app_context
    with app.app_context():
        # Usando a API para criar as entidades
        resp_doc = client.post("/doctors/", json={"first_name": "Dr. Grana", "last_name": "Alta", "email": "grana@email.com", "specialty": "Financeiro", "clinic_address": "Banco"})
        doc_id = resp_doc.get_json()["id"]
        resp_p1 = client.post("/patients/", json={"first_name": "Paciente", "last_name": "A", "phone": "A", "address": "A", "email": "A@email.com", "has_insurance": False})
        p1_id = resp_p1.get_json()["id"]
        resp_p2 = client.post("/patients/", json={"first_name": "Paciente", "last_name": "B", "phone": "B", "address": "B", "email": "B@email.com", "has_insurance": True})
        p2_id = resp_p2.get_json()["id"]

    # 2. Agenda consultas via API
    # Consulta 1: Preço original 200, pago 200 (sem convênio)
    client.post("/appointments/", json={"patient_id": p1_id, "doctor_id": doc_id, "date": "2025-10-01 11:00", "price": 200})
    # Consulta 2: Preço original 450, pago 225 (com convênio)
    client.post("/appointments/", json={"patient_id": p2_id, "doctor_id": doc_id, "date": "2025-10-01 12:00", "price": 450})

    # 3. Busca o médico e calcula o total
    with app.app_context():
        doctor = db.session.get(Doctor, doc_id)
        # 4. Verifica o total: 200.0 + 225.0 = 425.0
        assert doctor.total_earned() == 425.0