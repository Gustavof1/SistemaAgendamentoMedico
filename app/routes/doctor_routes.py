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
