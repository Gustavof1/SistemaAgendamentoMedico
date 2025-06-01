from flask import render_template, Blueprint, request, redirect, url_for
from .models.patient import Patient
from .models.doctor import Doctor
from .models.appointment import Appointment
from .utils import has_conflict
from .database import db
from datetime import datetime, timedelta

bp = Blueprint('views', __name__)

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/patients")
def list_patients():
    sort = request.args.get("sort", "first_name")
    patients = Patient.query.order_by(getattr(Patient, sort)).all()
    return render_template("list_patients.html", patients=patients, sort=sort)

@bp.route("/doctors")
def list_doctors():
    sort = request.args.get("sort", "first_name")
    doctors = Doctor.query.order_by(getattr(Doctor, sort)).all()
    return render_template("list_doctors.html", doctors=doctors, sort=sort)

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

@bp.route("/calendar")
def calendar():
    sort = request.args.get("sort", "date")
    appointments = Appointment.query.order_by(getattr(Appointment, sort)).all()
    doctors = {d.id: f"{d.first_name} {d.last_name}" for d in Doctor.query.all()}
    patients = {p.id: f"{p.first_name} {p.last_name}" for p in Patient.query.all()}
    return render_template("calendar.html", appointments=appointments, doctors=doctors, patients=patients, sort=sort)

@bp.route("/form/appointment", methods=["GET", "POST"])
def form_appointment():
    from .models.patient import Patient
    from .models.doctor import Doctor
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    conflict = False
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        date = request.form["date"]
        recurrence = request.form.get("recurrence", "once")
        # datetime-local retorna "YYYY-MM-DDTHH:MM", converter para "YYYY-MM-DD HH:MM"
        date_fmt = date.replace("T", " ") if "T" in date else date
        dates = []
        dt = datetime.strptime(date_fmt, "%Y-%m-%d %H:%M")
        if recurrence == "once":
            dates = [dt]
        else:
            interval = int(recurrence)
            for i in range(5):  # Limite de 5 ocorrências para evitar spam
                dates.append(dt + timedelta(days=interval * i))
        for d in dates:
            d_str = d.strftime("%Y-%m-%d %H:%M")
            if has_conflict(doctor_id, d_str):
                conflict = True
            db.session.add(Appointment(patient_id=patient_id, doctor_id=doctor_id, date=d_str))
        db.session.commit()
        return render_template("form_appointment.html", patients=patients, doctors=doctors, conflict=conflict, success=True)
    return render_template("form_appointment.html", patients=patients, doctors=doctors)

@bp.route("/edit/appointment/<int:id>", methods=["GET", "POST"])
def edit_appointment(id):
    appointment = db.session.get(Appointment, id)
    if not appointment:
        return "Consulta não encontrada", 404
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    conflict = False
    if request.method == "POST":
        date = request.form["date"]
        date_fmt = date.replace("T", " ") if "T" in date else date
        if has_conflict(appointment.doctor_id, date_fmt) and appointment.date != date_fmt:
            conflict = True
        appointment.date = date_fmt
        db.session.commit()
        return render_template("form_appointment.html", appointment=appointment, patients=patients, doctors=doctors, edit=True, conflict=conflict, success=True)
    return render_template("form_appointment.html", appointment=appointment, patients=patients, doctors=doctors, edit=True)
