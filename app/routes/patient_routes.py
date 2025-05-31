from flask import Blueprint, request, jsonify
from ..models.patient import Patient
from ..database import db

bp = Blueprint('patients', __name__, url_prefix='/patients')

@bp.route('/', methods=['POST'])
def create_patient():
    data = request.get_json()
    patient = Patient(
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data['phone'],
        address=data['address']
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "phone": patient.phone,
        "address": patient.address
    }), 201
