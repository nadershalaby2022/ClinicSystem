from flask import Flask, redirect, render_template, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config
import os
from sqlalchemy import inspect

# 1. تهيئة التطبيق وإدخال الإعدادات
app = Flask(__name__,
            template_folder='view',
            static_folder='static')
app.config.from_object(Config)

# 2. تهيئة الإضافات (قاعدة البيانات والاتصال الفوري)
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# التأكد من وجود مجلدات الرفع لمنع الأخطاء أثناء التشغيل الأول
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SPONSOR_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['BASE_DIR'], 'exports', 'excel'), exist_ok=True)
os.makedirs(os.path.join(app.config['BASE_DIR'], 'exports', 'reports', 'patients'), exist_ok=True)
os.makedirs(os.path.join(app.config['BASE_DIR'], 'exports', 'history'), exist_ok=True)

@app.route('/')
def index():
    if session.get('user_id'):
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_users'))
        if role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        if role == 'reception':
            return redirect(url_for('reception_dashboard'))
    return redirect(url_for('login'))

@app.errorhandler(403)
def forbidden(error):
    return render_template('common/error.html', code=403, message='ليس لديك صلاحية للوصول لهذه الصفحة'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('common/error.html', code=404, message='الصفحة المطلوبة غير موجودة'), 404

def initialize_database():
    from models.appointment import Appointment
    from models.medical_record import MedicalRecord
    from models.patient import Patient
    from models.queue import Queue
    from models.sponsor import Sponsor
    from models.user import User

    db.create_all()
    ensure_database_columns()
    for patient in Patient.query.filter(Patient.reference_number.is_(None)).all():
        patient.ensure_reference_number()
    db.session.commit()
    User.seed_defaults()

def ensure_database_columns():
    inspector = inspect(db.engine)
    patient_columns = {column['name'] for column in inspector.get_columns('patients')}
    if 'reference_number' not in patient_columns:
        with db.engine.begin() as connection:
            connection.exec_driver_sql('ALTER TABLE patients ADD COLUMN reference_number VARCHAR(30)')


# 🌟 التغيير هنا: استدعاء الـ Controllers أولاً
from controllers import admin_controller, auth_controller, doctor_controller, reception_controller, tv_controller


# 🌟 ثم تشغيل قاعدة البيانات في نهاية الملف تماماً لتجنب التداخل الدائري
with app.app_context():
    initialize_database()


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 نظام العيادة يعمل الآن محلياً!")
    print("💻 للدخول من جهاز السكرتارية/الطبيب: http://localhost:5000")
    print("🧾 لوحة الاستقبال: http://localhost:5000/reception")
    print("🩺 لوحة الطبيب: http://localhost:5000/doctor")
    print("📺 شاشة التلفزيون: http://localhost:5000/tv")
    print("="*50 + "\n")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)