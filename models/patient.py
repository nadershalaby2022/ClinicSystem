from datetime import datetime

from app import db


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(30), unique=True, nullable=True, index=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    phone = db.Column(db.String(40), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    appointments = db.relationship('Appointment', back_populates='patient', cascade='all, delete-orphan')
    queue_entries = db.relationship('Queue', back_populates='patient', cascade='all, delete-orphan')
    medical_records = db.relationship('MedicalRecord', back_populates='patient', cascade='all, delete-orphan')

    def ensure_reference_number(self):
        if not self.reference_number and self.id:
            self.reference_number = f'CL-{self.id:06d}'
        return self.reference_number

    def to_dict(self):
        self.ensure_reference_number()
        return {
            'id': self.id,
            'reference_number': self.reference_number,
            'name': self.name,
            'phone': self.phone,
            'age': self.age or '',
            'gender': self.gender or '',
            'address': self.address or '',
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
        }
