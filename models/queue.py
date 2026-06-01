from datetime import datetime

from app import db


class Queue(db.Model):
    __tablename__ = 'queue_entries'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True, index=True)
    ticket_number = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default='waiting', index=True)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    called_at = db.Column(db.DateTime, nullable=True)
    skipped_at = db.Column(db.DateTime, nullable=True)

    patient = db.relationship('Patient', back_populates='queue_entries')
    appointment = db.relationship('Appointment', back_populates='queue_entry')

    @property
    def status_label(self):
        return {
            'waiting': 'ينتظر',
            'serving': 'داخل الكشف',
            'done': 'تم الكشف',
            'cancelled': 'ملغي',
            'skipped': 'تم التخطي',
        }.get(self.status, self.status)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'appointment_id': self.appointment_id,
            'name': self.patient.name,
            'phone': self.patient.phone,
            'age': self.patient.age or '',
            'gender': self.patient.gender or '',
            'ticket': self.ticket_number,
            'ticket_number': self.ticket_number,
            'status': self.status,
            'status_label': self.status_label,
            'appointment_type': self.appointment.appointment_type if self.appointment else '',
            'entry_time': self.entry_time.strftime('%H:%M'),
        }
