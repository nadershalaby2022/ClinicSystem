from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(160), nullable=False)
    role = db.Column(db.String(30), nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    password_plain = db.Column(db.String(160), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    VALID_ROLES = ('admin', 'doctor', 'reception')

    def set_password(self, password):
        self.password_plain = password
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_label(self):
        return {
            'admin': 'مدير النظام',
            'doctor': 'طبيب',
            'reception': 'استقبال',
        }.get(self.role, self.role)

    def to_dict(self, include_password=False):
        data = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'role_label': self.role_label,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        if include_password:
            data['password_plain'] = self.password_plain
        return data

    @staticmethod
    def seed_defaults():
        defaults = [
            ('admin', 'مدير النظام', 'admin', 'admin123'),
            ('doctor', 'طبيب العيادة', 'doctor', 'doctor123'),
            ('reception', 'موظف الاستقبال', 'reception', 'reception123'),
        ]
        for username, full_name, role, password in defaults:
            if not User.query.filter_by(username=username).first():
                user = User(username=username, full_name=full_name, role=role, is_active=True)
                user.set_password(password)
                db.session.add(user)
        db.session.commit()
