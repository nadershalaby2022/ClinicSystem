from datetime import datetime, time

from app import db, socketio
from models.appointment import Appointment
from models.patient import Patient
from models.queue import Queue


def today_bounds():
    today = datetime.now().date()
    return datetime.combine(today, time.min), datetime.combine(today, time.max)


def next_ticket_number():
    start, end = today_bounds()
    last_entry = (
        Queue.query
        .filter(Queue.entry_time >= start, Queue.entry_time <= end)
        .order_by(Queue.ticket_number.desc())
        .first()
    )
    return (last_entry.ticket_number if last_entry else 0) + 1


def find_or_create_patient(data):
    phone = (data.get('phone') or '').strip()
    patient = Patient.query.filter_by(phone=phone).first() if phone else None
    if not patient:
        patient = Patient()
        db.session.add(patient)

    patient.name = (data.get('name') or '').strip()
    patient.phone = phone
    patient.age = int(data.get('age')) if str(data.get('age') or '').strip() else None
    patient.gender = data.get('gender') or ''
    patient.address = data.get('address') or ''
    patient.notes = data.get('patient_notes') or patient.notes
    return patient


def parse_appointment_time(value):
    if not value:
        return datetime.now()
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M')
    except ValueError:
        return datetime.now()


def create_appointment(data, user_id=None):
    patient = find_or_create_patient(data)
    appointment = Appointment(
        patient=patient,
        appointment_type=data.get('appointment_type') or 'كشف',
        appointment_time=parse_appointment_time(data.get('appointment_time')),
        status='waiting',
        notes=data.get('notes') or '',
        created_by_id=user_id,
    )
    db.session.add(appointment)
    db.session.flush()
    patient.ensure_reference_number()

    queue_entry = Queue(
        patient=patient,
        appointment=appointment,
        ticket_number=next_ticket_number(),
        status='waiting',
        entry_time=datetime.now(),
    )
    db.session.add(queue_entry)
    db.session.commit()
    broadcast_queue_update()
    return appointment


def update_appointment(appointment_id, data):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return None

    patient = appointment.patient
    patient.name = (data.get('name') or patient.name).strip()
    patient.phone = (data.get('phone') or patient.phone).strip()
    patient.age = int(data.get('age')) if str(data.get('age') or '').strip() else None
    patient.gender = data.get('gender') or patient.gender
    patient.address = data.get('address') or patient.address
    patient.notes = data.get('patient_notes') or patient.notes

    appointment.appointment_type = data.get('appointment_type') or appointment.appointment_type
    appointment.appointment_time = parse_appointment_time(data.get('appointment_time'))
    appointment.notes = data.get('notes') or ''

    db.session.commit()
    broadcast_queue_update()
    return appointment


def cancel_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return None
    appointment.status = 'cancelled'
    if appointment.queue_entry:
        appointment.queue_entry.status = 'cancelled'
    db.session.commit()
    broadcast_queue_update()
    return appointment


def call_patient(queue_id):
    queue_entry = db.session.get(Queue, queue_id)
    if not queue_entry:
        return None

    previous = Queue.query.filter_by(status='serving').all()
    for entry in previous:
        entry.status = 'done'
        if entry.appointment:
            entry.appointment.status = 'done'

    queue_entry.status = 'serving'
    queue_entry.called_at = datetime.now()
    if queue_entry.appointment:
        queue_entry.appointment.status = 'serving'

    db.session.commit()
    broadcast_queue_update()
    return queue_entry


def skip_patient(queue_id):
    queue_entry = db.session.get(Queue, queue_id)
    if not queue_entry:
        return None
    queue_entry.status = 'skipped'
    queue_entry.skipped_at = datetime.now()
    if queue_entry.appointment:
        queue_entry.appointment.status = 'skipped'
    db.session.commit()
    broadcast_queue_update()
    return queue_entry


def mark_patient_done(patient_id):
    active_entries = Queue.query.filter_by(patient_id=patient_id, status='serving').all()
    for entry in active_entries:
        entry.status = 'done'
        if entry.appointment:
            entry.appointment.status = 'done'
    db.session.commit()
    broadcast_queue_update()


def queue_snapshot(include_all=False):
    start, end = today_bounds()
    base_query = Queue.query.filter(Queue.entry_time >= start, Queue.entry_time <= end)
    serving = base_query.filter_by(status='serving').order_by(Queue.called_at.desc()).first()
    waiting = base_query.filter_by(status='waiting').order_by(Queue.ticket_number.asc()).all()
    skipped = base_query.filter_by(status='skipped').order_by(Queue.ticket_number.asc()).all()
    done = base_query.filter_by(status='done').order_by(Queue.ticket_number.asc()).all() if include_all else []

    return {
        'current': serving.to_dict() if serving else None,
        'current_number': serving.ticket_number if serving else '-',
        'current_name': serving.patient.name if serving else 'لا يوجد حالياً',
        'waiting': [entry.to_dict() for entry in waiting],
        'next_patients': [entry.to_dict() for entry in waiting],
        'skipped': [entry.to_dict() for entry in skipped],
        'done': [entry.to_dict() for entry in done],
        'updated_at': datetime.now().strftime('%H:%M:%S'),
    }


def today_appointments():
    start, end = today_bounds()
    appointments = (
        Appointment.query
        .filter(Appointment.appointment_time >= start, Appointment.appointment_time <= end)
        .order_by(Appointment.appointment_time.asc())
        .all()
    )
    return [appointment.to_dict() for appointment in appointments]


def broadcast_queue_update():
    socketio.emit('queue_update', queue_snapshot(include_all=True))
