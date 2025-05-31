from app import create_app
from app.database import db

def test_create_patient():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        response = client.post("/patients/", json={
            "first_name": "Maria",
            "last_name": "Silva",
            "phone": "11999999999",
            "address": "Rua A, 123",
            "email": "maria@teste.com"
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data["first_name"] == "Maria"
        assert data["email"] == "maria@teste.com"

def test_edit_patient():
    app = create_app()
    client = app.test_client()
    with app.app_context():
        db.drop_all()
        db.create_all()
        resp = client.post("/patients/", json={
            "first_name": "Carlos",
            "last_name": "Pereira",
            "phone": "11988888888",
            "address": "Rua B, 456",
            "email": "carlos@teste.com"
        })
        pid = resp.get_json()["id"]
        response = client.put(f"/patients/{pid}", json={
            "first_name": "Carlos",
            "last_name": "Pereira",
            "phone": "11988888888",
            "address": "Rua Nova, 789",
            "email": "carloseditado@teste.com"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["address"] == "Rua Nova, 789"
        assert data["email"] == "carloseditado@teste.com"
