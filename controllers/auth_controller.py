from functools import wraps

from flask import abort, redirect, render_template, request, session, url_for

from app import app, db
from models.user import User


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user():
            return redirect(url_for('login', next=request.path))
        return view_func(*args, **kwargs)
    return wrapped_view


def roles_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            user = current_user()
            if not user:
                return redirect(url_for('login', next=request.path))
            if user.role not in roles:
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator


@app.context_processor
def inject_current_user():
    return {'current_user': current_user()}


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user():
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if not user or not user.is_active or not user.check_password(password):
            error = 'بيانات الدخول غير صحيحة أو الحساب غير مفعل'
        else:
            session.clear()
            session['user_id'] = user.id
            session['role'] = user.role
            session['full_name'] = user.full_name
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(url_for('index'))

    return render_template('common/login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('common/dashboard.html')
