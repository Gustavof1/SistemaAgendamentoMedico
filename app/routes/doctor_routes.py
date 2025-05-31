from flask import Blueprint, request, jsonify
from ..models.doctor import Doctor
from ..database import db

bp = Blueprint('doctors', __name__, url_prefix='/doctors')

@bp.route('/', methods=['POST'])
def create_doctor():
    data = request.json
    doctor = Doctor(name=data['name'])
    db.session.add(doctor)
    db.session.commit()
    return jsonify({"id": doctor.id, "name": doctor.name}), 201
