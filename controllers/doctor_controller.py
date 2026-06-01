from flask import jsonify, render_template, request, send_file, session
from sqlalchemy import or_

from app import app, db
from controllers.auth_controller import roles_required
from models.medical_record import MedicalRecord
from models.patient import Patient
from services.queue_service import mark_patient_done, queue_snapshot, today_appointments
from services.report_service import create_medical_record, prescription_html


@app.route('/doctor')
@roles_required('admin', 'doctor')
def doctor_dashboard():
    return render_template('doctor/doctor_dashboard.html')


@app.route('/doctor/patients')
@roles_required('admin', 'doctor')
def doctor_patient_search():
    return render_template('doctor/patient_search.html')


@app.route('/api/doctor/patients/search')
@roles_required('admin', 'doctor')
def api_search_patients():
    query = (request.args.get('q') or '').strip()
    patients_query = Patient.query
    if query:
        pattern = f'%{query}%'
        patients_query = patients_query.filter(or_(
            Patient.name.ilike(pattern),
            Patient.phone.ilike(pattern),
            Patient.reference_number.ilike(pattern),
        ))
    patients = patients_query.order_by(Patient.updated_at.desc()).limit(50).all()
    results = []
    for patient in patients:
        last_record = (
            MedicalRecord.query
            .filter_by(patient_id=patient.id)
            .order_by(MedicalRecord.created_at.desc())
            .first()
        )
        data = patient.to_dict()
        data['visits_count'] = len(patient.medical_records)
        data['last_visit'] = last_record.created_at.strftime('%Y-%m-%d %H:%M') if last_record else ''
        data['last_diagnosis'] = last_record.diagnosis if last_record else ''
        results.append(data)
    return jsonify({'patients': results})


@app.route('/api/doctor/state')
@roles_required('admin', 'doctor')
def api_doctor_state():
    return jsonify({
        'queue': queue_snapshot(include_all=True),
        'appointments': today_appointments(),
    })


@app.route('/doctor/patient/<int:patient_id>')
@roles_required('admin', 'doctor')
def doctor_patient_profile(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return render_template('common/error.html', code=404, message='ملف المريض غير موجود'), 404
    records = (
        MedicalRecord.query
        .filter_by(patient_id=patient.id)
        .order_by(MedicalRecord.created_at.desc())
        .all()
    )
    return render_template('doctor/patient_profile.html', patient=patient, records=records)


@app.route('/api/doctor/patient/<int:patient_id>/records', methods=['POST'])
@roles_required('admin', 'doctor')
def api_create_medical_record(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'success': False, 'message': 'ملف المريض غير موجود'}), 404

    data = request.get_json(silent=True) or {}
    record = create_medical_record(patient, session.get('user_id'), data)
    if data.get('finish_visit'):
        mark_patient_done(patient.id)
    return jsonify({'success': True, 'record': record.to_dict(), 'print_url': f'/doctor/prescription/{record.id}/print'})


@app.route('/doctor/prescription/<int:record_id>/print')
@roles_required('admin', 'doctor')
def print_prescription(record_id):
    record = db.session.get(MedicalRecord, record_id)
    if not record:
        return render_template('common/error.html', code=404, message='الروشتة غير موجودة'), 404
    return prescription_html(record)


@app.route('/doctor/prescription/<int:record_id>/download')
@roles_required('admin', 'doctor')
def download_prescription(record_id):
    record = db.session.get(MedicalRecord, record_id)
    if not record or not record.prescription_file:
        return render_template('common/error.html', code=404, message='ملف الروشتة غير موجود'), 404
    return send_file(record.prescription_file, as_attachment=True)
