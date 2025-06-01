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
        assert response.get_json()["first_name"] == "João"

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
