from flask import Blueprint, request, jsonify
from ..models.patient import Patient
from ..database import db

bp = Blueprint('patients', __name__, url_prefix='/patients')

@bp.route('/', methods=['POST'])
def create_patient():
    data = request.get_json()
    required = ['first_name', 'last_name', 'phone', 'address', 'email']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Campo obrigatorio ausente: {field}"}), 400
    patient = Patient(
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data['phone'],
        address=data['address'],
        email=data.get('email'),
        has_insurance=data.get('has_insurance', False)
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "phone": patient.phone,
        "address": patient.address,
        "email": patient.email,
        "has_insurance": patient.has_insurance
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
def edit_patient(id):
    data = request.get_json()
    patient = db.session.get(Patient, id)
    if not patient:
        return jsonify({"error": "Paciente nao encontrado"}), 404
    for field in ['first_name', 'last_name', 'phone', 'address', 'email']:
        if field in data and not data[field]:
            return jsonify({"error": f"Campo obrigatorio ausente: {field}"}), 400
    patient.first_name = data.get('first_name', patient.first_name)
    patient.last_name = data.get('last_name', patient.last_name)
    patient.phone = data.get('phone', patient.phone)
    patient.address = data.get('address', patient.address)
    patient.email = data.get('email', patient.email)
    if 'has_insurance' in data:
        patient.has_insurance = data['has_insurance']
    db.session.commit()
    return jsonify({
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "phone": patient.phone,
        "address": patient.address,
        "email": patient.email,
        "has_insurance": patient.has_insurance
    })
