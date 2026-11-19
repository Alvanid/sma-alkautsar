from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    
    # Initialize CSRF Protection (WAJIB untuk csrf_token())
    csrf = CSRFProtect(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp
    from routes.attendance import attendance_bp
    from routes.reports import reports_bp
    from routes.permissions import permissions_bp
    from routes.settings import settings_bp
    from routes.principal import principal_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(permissions_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(principal_bp)
    
    # Main routes
    @app.route('/')
    def landing():
        return render_template('landing.html')
    
    @app.route('/dashboard')
    def dashboard():
        from flask_login import current_user
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        elif current_user.role == 'principal':
            return redirect(url_for('principal.dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)