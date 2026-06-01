from datetime import datetime

from app import db


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    symptoms = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    prescription_file = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)

    patient = db.relationship('Patient', back_populates='medical_records')
    doctor = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor': self.doctor.full_name if self.doctor else '',
            'symptoms': self.symptoms or '',
            'diagnosis': self.diagnosis or '',
            'prescription': self.prescription or '',
            'notes': self.notes or '',
            'prescription_file': self.prescription_file or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
        }
