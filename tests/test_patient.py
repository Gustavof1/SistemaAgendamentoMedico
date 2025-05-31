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
            "address": "Rua A, 123"
        })
        assert response.status_code == 201
        assert response.get_json()["name"] == "Maria"
