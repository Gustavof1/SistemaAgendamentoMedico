from app import create_app
from app.database import db

def test_create_doctor():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        response = client.post("/doctors/", json={
            "first_name": "João",
            "last_name": "Souza",
            "clinic_address": "Av. Central, 456",
            "specialty": "Cardiologia",
            "email": "joaosouza@email.com"
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data["first_name"] == "João"
        assert data["specialty"] == "Cardiologia"
        assert data["email"] == "joaosouza@email.com"

def test_create_doctor_missing_fields():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Faltando specialty
        resp = client.post("/doctors/", json={
            "first_name": "Maria",
            "last_name": "Silva",
            "clinic_address": "Rua XPTO",
            "email": "maria@teste.com"
        })
        assert resp.status_code == 400
        assert b"Campo obrigatorio ausente" in resp.data
        # Faltando email
        resp2 = client.post("/doctors/", json={
            "first_name": "Carlos",
            "last_name": "Oliveira",
            "clinic_address": "Rua YYY",
            "specialty": "Ortopedia"
        })
        assert resp2.status_code == 400
        assert b"Campo obrigatorio ausente" in resp2.data

def test_edit_doctor():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        resp = client.post("/doctors/", json={
            "first_name": "Pedro",
            "last_name": "Almeida",
            "clinic_address": "Rua X, 123",
            "specialty": "Cardiologia",
            "email": "pedroalmeida@email.com"
        })
        did = resp.get_json()["id"]
        response = client.put(f"/doctors/{did}", json={
            "first_name": "Pedro",
            "last_name": "Almeida",
            "clinic_address": "Rua Y, 999",
            "specialty": "Cardiologia",
            "email": "pedroalmeida@email.com"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["clinic_address"] == "Rua Y, 999"
