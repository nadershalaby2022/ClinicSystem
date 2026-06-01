from datetime import datetime

from app import db


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    appointment_type = db.Column(db.String(40), nullable=False, default='كشف')
    appointment_time = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    status = db.Column(db.String(30), nullable=False, default='waiting', index=True)
    notes = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    patient = db.relationship('Patient', back_populates='appointments')
    created_by = db.relationship('User')
    queue_entry = db.relationship('Queue', back_populates='appointment', uselist=False, cascade='all, delete-orphan')

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
            'patient': self.patient.to_dict(),
            'appointment_type': self.appointment_type,
            'appointment_time': self.appointment_time.strftime('%Y-%m-%dT%H:%M'),
            'appointment_time_label': self.appointment_time.strftime('%Y-%m-%d %H:%M'),
            'status': self.status,
            'status_label': self.status_label,
            'notes': self.notes or '',
            'queue_id': self.queue_entry.id if self.queue_entry else None,
            'ticket_number': self.queue_entry.ticket_number if self.queue_entry else None,
        }
