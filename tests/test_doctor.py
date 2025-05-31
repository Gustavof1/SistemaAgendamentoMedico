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
            "clinic_address": "Av. Central, 456"
        })
        assert response.status_code == 201
        assert response.get_json()["name"] == "Dr. João"
