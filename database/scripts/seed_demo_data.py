from datetime import datetime, timedelta
import os
import shutil
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app, db
from models.appointment import Appointment
from models.medical_record import MedicalRecord
from models.patient import Patient
from models.queue import Queue
from models.user import User
from services.report_service import save_prescription_file


DEMO_PATIENTS = [
    ('أحمد سمير عبد الله', '01010000001', 34, 'ذكر', 'مدينة نصر', 'كشف', 'done_today'),
    ('منى خالد محمود', '01010000002', 29, 'أنثى', 'مصر الجديدة', 'استشارة', 'done_today'),
    ('حسام عادل يوسف', '01010000003', 46, 'ذكر', 'المعادي', 'كشف', 'done_today'),
    ('سارة مصطفى علي', '01010000004', 31, 'أنثى', 'العباسية', 'كشف', 'done_yesterday'),
    ('كريم محمد فؤاد', '01010000005', 52, 'ذكر', 'شبرا', 'استشارة', 'done_yesterday'),
    ('نجلاء حسن إبراهيم', '01010000006', 41, 'أنثى', 'الهرم', 'كشف', 'done_yesterday'),
    ('يوسف محمود سالم', '01010000007', 27, 'ذكر', 'التجمع الخامس', 'كشف', 'serving'),
    ('ليلى أحمد فاروق', '01010000008', 36, 'أنثى', 'الدقي', 'كشف', 'waiting'),
    ('محمود فتحي منصور', '01010000009', 58, 'ذكر', 'حلوان', 'استشارة', 'waiting'),
    ('هبة سامي كامل', '01010000010', 24, 'أنثى', 'الزمالك', 'كشف', 'waiting'),
    ('طارق أمين شوقي', '01010000011', 63, 'ذكر', 'المقطم', 'كشف', 'waiting'),
]


def clear_demo_data():
    for model in (MedicalRecord, Queue, Appointment, Patient):
        db.session.query(model).delete()
    db.session.commit()

    history_dir = os.path.join(app.config['BASE_DIR'], 'exports', 'history')
    os.makedirs(history_dir, exist_ok=True)
    for name in os.listdir(history_dir):
        path = os.path.abspath(os.path.join(history_dir, name))
        if path.startswith(os.path.abspath(history_dir)) and os.path.isdir(path):
            shutil.rmtree(path)


def create_patient(name, phone, age, gender, address):
    patient = Patient(name=name, phone=phone, age=age, gender=gender, address=address)
    db.session.add(patient)
    db.session.flush()
    patient.ensure_reference_number()
    return patient


def create_visit_record(patient, doctor, visit_date, diagnosis):
    record = MedicalRecord(
        patient=patient,
        doctor_id=doctor.id,
        symptoms='صداع وإرهاق بسيط مع مراجعة العلامات الحيوية.',
        diagnosis=diagnosis,
        prescription='دواء تجريبي 1: قرص بعد الأكل مرتين يومياً\nدواء تجريبي 2: عند اللزوم\nمراجعة بعد أسبوع عند الحاجة.',
        notes='بيانات تجريبية لاختبار النظام والطباعة والهيستوري.',
        created_at=visit_date,
    )
    db.session.add(record)
    db.session.commit()
    save_prescription_file(record)
    return record


def seed():
    doctor = User.query.filter_by(role='doctor').first()
    reception = User.query.filter_by(role='reception').first()
    now = datetime.now().replace(second=0, microsecond=0)
    yesterday = now - timedelta(days=1)
    today_ticket = 1
    yesterday_ticket = 1

    for name, phone, age, gender, address, appointment_type, state in DEMO_PATIENTS:
        patient = create_patient(name, phone, age, gender, address)

        if state == 'done_yesterday':
            appointment_time = yesterday.replace(hour=10 + yesterday_ticket, minute=0)
            ticket_number = yesterday_ticket
            yesterday_ticket += 1
            status = 'done'
        else:
            appointment_time = now.replace(hour=9, minute=0) + timedelta(minutes=20 * (today_ticket - 1))
            ticket_number = today_ticket
            today_ticket += 1
            status = 'serving' if state == 'serving' else ('done' if state == 'done_today' else 'waiting')

        appointment = Appointment(
            patient=patient,
            appointment_type=appointment_type,
            appointment_time=appointment_time,
            status=status,
            notes='بيانات تجريبية للتشغيل',
            created_by_id=reception.id if reception else None,
        )
        db.session.add(appointment)
        db.session.flush()

        queue_entry = Queue(
            patient=patient,
            appointment=appointment,
            ticket_number=ticket_number,
            status=status,
            entry_time=appointment_time,
            called_at=appointment_time + timedelta(minutes=5) if status in ('serving', 'done') else None,
        )
        db.session.add(queue_entry)
        db.session.commit()

        if state == 'done_today':
            create_visit_record(patient, doctor, appointment_time + timedelta(minutes=18), 'كشف تجريبي مكتمل اليوم')
        elif state == 'done_yesterday':
            create_visit_record(patient, doctor, appointment_time + timedelta(minutes=18), 'كشف تجريبي مكتمل أمس')


if __name__ == '__main__':
    with app.app_context():
        clear_demo_data()
        seed()
        print('تم إدخال بيانات التجربة بنجاح: 11 مريضاً حسب التقسيمة المطلوبة.')
