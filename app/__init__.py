from flask import Flask
from .database import db

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///appointments.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        from .models import patient, doctor, appointment
        db.create_all()

    from .routes import patient_routes, doctor_routes, appointment_routes
    app.register_blueprint(patient_routes.bp)
    app.register_blueprint(doctor_routes.bp)
    app.register_blueprint(appointment_routes.bp)

    from .views import bp as views_bp, init_app
    app.register_blueprint(views_bp)
    init_app(app)  # registra o filtro datetimeformat

    return app
