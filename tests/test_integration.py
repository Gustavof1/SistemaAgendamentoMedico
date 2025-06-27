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
