import os

class Config:
    # تحديد المسار الرئيسي للمشروع ديناميكياً
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # مفتاح الأمان لتشفير الجلسات (Sessions) والكوكيز محلياً
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clinic-cyber-security-key-2026'
    
    # مسار قاعدة بيانات SQLite المحلية داخل مجلد database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'clinic.db')}"
    
    # إيقاف تتبع التعديلات لتوفير استهلاك الذاكرة والمعالج على الجهاز المحلي
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # مسارات رفع الملفات (الشعارات، الختم، الإعلانات)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'assets', 'uploads')
    SPONSOR_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'sponsors')
    
    # أقصى حجم للملفات المرفوعة (16 ميجابايت مثلاً لحماية الذاكرة)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024