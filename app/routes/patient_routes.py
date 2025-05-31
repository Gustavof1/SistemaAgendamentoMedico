from flask import Blueprint, request, jsonify
from ..models.patient import Patient
from ..database import db

bp = Blueprint('patients', __name__, url_prefix='/patients')

@bp.route('/', methods=['POST'])
def create_patient():
    data = request.json
    patient = Patient(name=data['name'])
    db.session.add(patient)
    db.session.commit()
    return jsonify({"id": patient.id, "name": patient.name}), 201
