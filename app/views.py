from flask import render_template, Blueprint, request, redirect, url_for
from .models.patient import Patient
from .models.doctor import Doctor
from .models.appointment import Appointment
from .utils import has_conflict
from .database import db

bp = Blueprint('views', __name__)

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/patients")
def list_patients():
    sort = request.args.get("sort", "first_name")
    patients = Patient.query.order_by(getattr(Patient, sort)).all()
    return render_template("list_patients.html", patients=patients)

@bp.route("/doctors")
def list_doctors():
    sort = request.args.get("sort", "first_name")
    doctors = Doctor.query.order_by(getattr(Doctor, sort)).all()
    return render_template("list_doctors.html", doctors=doctors)

@bp.route("/form/patient", methods=["GET", "POST"])
def form_patient():
    if request.method == "POST":
        p = Patient(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            phone=request.form["phone"],
            address=request.form["address"],
            email=request.form.get("email")
        )
        db.session.add(p)
        db.session.commit()
        return redirect("/patients")
    return render_template("form_patient.html")

@bp.route("/edit/patient/<int:id>", methods=["GET", "POST"])
def edit_patient(id):
    patient = db.session.get(Patient, id)
    if not patient:
        return "Paciente não encontrado", 404
    if request.method == "POST":
        patient.first_name = request.form["first_name"]
        patient.last_name = request.form["last_name"]
        patient.phone = request.form["phone"]
        patient.address = request.form["address"]
        patient.email = request.form.get("email")
        db.session.commit()
        return redirect("/patients")
    return render_template("form_patient.html", patient=patient, edit=True)

@bp.route("/form/doctor", methods=["GET", "POST"])
def form_doctor():
    if request.method == "POST":
        d = Doctor(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            clinic_address=request.form["clinic_address"]
        )
        db.session.add(d)
        db.session.commit()
        return redirect("/doctors")
    return render_template("form_doctor.html")

@bp.route("/edit/doctor/<int:id>", methods=["GET", "POST"])
def edit_doctor(id):
    doctor = db.session.get(Doctor, id)
    if not doctor:
        return "Médico não encontrado", 404
    if request.method == "POST":
        doctor.first_name = request.form["first_name"]
        doctor.last_name = request.form["last_name"]
        doctor.clinic_address = request.form["clinic_address"]
        db.session.commit()
        return redirect("/doctors")
    return render_template("form_doctor.html", doctor=doctor, edit=True)

@bp.route("/delete/patient/<int:id>")
def delete_patient(id):
    patient = db.session.get(Patient, id)
    if not patient:
        return redirect("/patients")
    db.session.delete(patient)
    db.session.commit()
    return redirect("/patients")

@bp.route("/delete/doctor/<int:id>")
def delete_doctor(id):
    doctor = db.session.get(Doctor, id)
    if not doctor:
        return redirect("/doctors")
    db.session.delete(doctor)
    db.session.commit()
    return redirect("/doctors")

@bp.route("/form/appointment", methods=["GET", "POST"])
def form_appointment():
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        date = request.form["date"]
        if has_conflict(doctor_id, date):
            return "Conflito de horário", 409
        db.session.add(Appointment(patient_id=patient_id, doctor_id=doctor_id, date=date))
        db.session.commit()
        return redirect("/")
    return render_template("form_appointment.html")
