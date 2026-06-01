from flask import jsonify, redirect, render_template, request, send_file, session, url_for

from app import app, db
from controllers.auth_controller import roles_required
from models.user import User
from services.report_service import export_patients_xlsx


def user_payload():
    data = request.get_json(silent=True) or {}
    return {
        'username': (data.get('username') or '').strip(),
        'full_name': (data.get('full_name') or '').strip(),
        'role': data.get('role') or 'reception',
        'password': data.get('password') or '',
        'is_active': bool(data.get('is_active', True)),
    }


def validate_user(data, require_password=True):
    if not data['username'] or not data['full_name'] or data['role'] not in User.VALID_ROLES:
        return 'برجاء إدخال اسم المستخدم والاسم الكامل والدور بشكل صحيح'
    if require_password and not data['password']:
        return 'برجاء إدخال كلمة المرور'
    return None


@app.route('/admin')
@roles_required('admin')
def admin_index():
    return redirect(url_for('admin_users'))


@app.route('/admin/users')
@roles_required('admin')
def admin_users():
    return render_template('admin/users.html')


@app.route('/api/admin/users', methods=['GET'])
@roles_required('admin')
def api_list_users():
    users = User.query.order_by(User.created_at.asc()).all()
    return jsonify({'users': [user.to_dict(include_password=True) for user in users]})


@app.route('/api/admin/users', methods=['POST'])
@roles_required('admin')
def api_create_user():
    data = user_payload()
    error = validate_user(data)
    if error:
        return jsonify({'success': False, 'message': error}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'اسم المستخدم موجود بالفعل'}), 400

    user = User(username=data['username'], full_name=data['full_name'], role=data['role'], is_active=data['is_active'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'user': user.to_dict(include_password=True)})


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@roles_required('admin')
def api_update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'message': 'المستخدم غير موجود'}), 404

    data = user_payload()
    error = validate_user(data, require_password=False)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    duplicate = User.query.filter(User.username == data['username'], User.id != user.id).first()
    if duplicate:
        return jsonify({'success': False, 'message': 'اسم المستخدم موجود بالفعل'}), 400

    user.username = data['username']
    user.full_name = data['full_name']
    user.role = data['role']
    user.is_active = data['is_active']
    if data['password']:
        user.set_password(data['password'])
    db.session.commit()
    return jsonify({'success': True, 'user': user.to_dict(include_password=True)})


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@roles_required('admin')
def api_delete_user(user_id):
    if user_id == session.get('user_id'):
        return jsonify({'success': False, 'message': 'لا يمكن حذف المستخدم الحالي أثناء تسجيل الدخول'}), 400
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'message': 'المستخدم غير موجود'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/export/patients.xlsx')
@roles_required('admin')
def export_patients():
    path = export_patients_xlsx()
    return send_file(path, as_attachment=True, download_name='patients.xlsx')
