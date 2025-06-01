from flask import Blueprint, request, jsonify
from ..models.doctor import Doctor
from ..database import db

bp = Blueprint('doctors', __name__, url_prefix='/doctors')

@bp.route('/', methods=['POST'])
def create_doctor():
    data = request.get_json()
    required = ['first_name', 'last_name', 'clinic_address', 'specialty', 'email']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Campo obrigatorio ausente: {field}"}), 400
    doctor = Doctor(
        first_name=data['first_name'],
        last_name=data['last_name'],
        clinic_address=data['clinic_address'],
        specialty=data['specialty'],
        email=data['email']
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify({
        "id": doctor.id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "clinic_address": doctor.clinic_address,
        "specialty": doctor.specialty,
        "email": doctor.email
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
def edit_doctor(id):
    data = request.get_json()
    doctor = db.session.get(Doctor, id)
    if not doctor:
        return jsonify({"error": "Medico nao encontrado"}), 404
    for field in ['first_name', 'last_name', 'clinic_address', 'specialty', 'email']:
        if field in data and not data[field]:
            return jsonify({"error": f"Campo obrigatorio ausente: {field}"}), 400
    doctor.first_name = data.get('first_name', doctor.first_name)
    doctor.last_name = data.get('last_name', doctor.last_name)
    doctor.clinic_address = data.get('clinic_address', doctor.clinic_address)
    doctor.specialty = data.get('specialty', doctor.specialty)
    doctor.email = data.get('email', doctor.email)
    db.session.commit()
    return jsonify({
        "id": doctor.id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "clinic_address": doctor.clinic_address,
        "specialty": doctor.specialty,
        "email": doctor.email
    })
