from flask import Blueprint, request, jsonify
from ..models.doctor import Doctor
from ..database import db

bp = Blueprint('doctors', __name__, url_prefix='/doctors')

@bp.route('/', methods=['POST'])
def create_doctor():
    data = request.get_json()
    doctor = Doctor(
        first_name=data['first_name'],
        last_name=data['last_name'],
        clinic_address=data['clinic_address']
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify({
        "id": doctor.id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "clinic_address": doctor.clinic_address
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
def edit_doctor(id):
    data = request.get_json()
    doctor = db.session.get(Doctor, id)
    if not doctor:
        return jsonify({"error": "Médico não encontrado"}), 404
    doctor.first_name = data.get('first_name', doctor.first_name)
    doctor.last_name = data.get('last_name', doctor.last_name)
    doctor.clinic_address = data.get('clinic_address', doctor.clinic_address)
    db.session.commit()
    return jsonify({
        "id": doctor.id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "clinic_address": doctor.clinic_address
    })
