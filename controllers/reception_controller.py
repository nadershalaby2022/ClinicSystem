from flask import jsonify, render_template, request, session

from app import app, db
from controllers.auth_controller import roles_required
from services.queue_service import (
    call_patient,
    cancel_appointment,
    create_appointment,
    queue_snapshot,
    skip_patient,
    today_appointments,
    update_appointment,
)


def validate_booking_payload(data):
    required = ('name', 'phone', 'appointment_type')
    missing = [field for field in required if not (data.get(field) or '').strip()]
    if missing:
        return 'برجاء إدخال اسم المريض ورقم الهاتف ونوع الحجز'
    return None


@app.route('/reception')
@roles_required('admin', 'reception')
def reception_dashboard():
    return render_template('reception/reception_dashboard.html')


@app.route('/api/queue')
def api_queue_snapshot():
    return jsonify(queue_snapshot(include_all=True))


@app.route('/api/reception/state')
@roles_required('admin', 'reception')
def api_reception_state():
    return jsonify({
        'queue': queue_snapshot(include_all=True),
        'appointments': today_appointments(),
    })


@app.route('/api/reception/appointments', methods=['POST'])
@roles_required('admin', 'reception')
def api_create_appointment():
    data = request.get_json(silent=True) or {}
    error = validate_booking_payload(data)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    try:
        appointment = create_appointment(data, user_id=session.get('user_id'))
        return jsonify({'success': True, 'appointment': appointment.to_dict()})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(exc)}), 500


@app.route('/api/reception/appointments/<int:appointment_id>', methods=['PUT'])
@roles_required('admin', 'reception')
def api_update_appointment(appointment_id):
    data = request.get_json(silent=True) or {}
    error = validate_booking_payload(data)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    appointment = update_appointment(appointment_id, data)
    if not appointment:
        return jsonify({'success': False, 'message': 'الحجز غير موجود'}), 404
    return jsonify({'success': True, 'appointment': appointment.to_dict()})


@app.route('/api/reception/appointments/<int:appointment_id>', methods=['DELETE'])
@roles_required('admin', 'reception')
def api_cancel_appointment(appointment_id):
    appointment = cancel_appointment(appointment_id)
    if not appointment:
        return jsonify({'success': False, 'message': 'الحجز غير موجود'}), 404
    return jsonify({'success': True})


@app.route('/api/reception/call/<int:queue_id>', methods=['POST'])
@roles_required('admin', 'reception')
def api_call_patient(queue_id):
    entry = call_patient(queue_id)
    if not entry:
        return jsonify({'success': False, 'message': 'الحالة غير موجودة'}), 404
    return jsonify({'success': True, 'entry': entry.to_dict()})


@app.route('/api/reception/skip/<int:queue_id>', methods=['POST'])
@roles_required('admin', 'reception')
def api_skip_patient(queue_id):
    entry = skip_patient(queue_id)
    if not entry:
        return jsonify({'success': False, 'message': 'الحالة غير موجودة'}), 404
    return jsonify({'success': True, 'entry': entry.to_dict()})
