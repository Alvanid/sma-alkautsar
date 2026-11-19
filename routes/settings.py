from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from . import settings_bp
from models import db, SystemSetting, Backup, Holiday
# Gunakan alias 'as' untuk menghindari bentrok nama dengan fungsi route
from services.backup_service import create_backup as svc_create_backup, restore_backup as svc_restore_backup
from config import Config
from datetime import datetime
import os

@settings_bp.route('/')
@login_required
def index():
    settings = {s.key: s.value for s in SystemSetting.query.all()}
    return render_template('settings/index.html', settings=settings)

@settings_bp.route('/update', methods=['POST'])
@login_required
def update():
    for key, value in request.form.items():
        if key.startswith('setting_'):
            setting_key = key.replace('setting_', '')
            setting = SystemSetting.query.filter_by(key=setting_key).first()
            if setting:
                setting.value = value
            else:
                setting = SystemSetting(key=setting_key, value=value)
                db.session.add(setting)
    db.session.commit()
    flash('Pengaturan diperbarui', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/backup')
@login_required
def backup():
    backups = Backup.query.order_by(Backup.created_at.desc()).all()
    return render_template('settings/backup.html', backups=backups)

@settings_bp.route('/backup/create', methods=['POST'])
@login_required
def create_backup():
    # Perbaikan path absolut untuk Windows
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_path = os.path.abspath(db_uri.replace('sqlite:///', ''))
    
    # Panggil fungsi service dengan alias
    backup_record = svc_create_backup(current_user.id, db_path, Config.BACKUP_FOLDER)
    flash('Backup berhasil dibuat', 'success')
    return redirect(url_for('settings.backup'))

@settings_bp.route('/backup/<int:id>/download')
@login_required
def download_backup(id):
    backup_record = Backup.query.get_or_404(id)
    filepath = os.path.join(Config.BACKUP_FOLDER, backup_record.filename)
    return send_file(filepath, as_attachment=True)

@settings_bp.route('/backup/<int:id>/restore', methods=['POST'])
@login_required
def restore_backup(id):
    if current_user.role != 'admin':
        flash('Hanya admin yang dapat restore', 'danger')
        return redirect(url_for('settings.backup'))
    
    # Perbaikan path absolut untuk Windows
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_path = os.path.abspath(db_uri.replace('sqlite:///', ''))
    
    # Panggil fungsi service dengan alias
    success = svc_restore_backup(id, db_path, Config.BACKUP_FOLDER)
    if success:
        flash('Database berhasil di-restore. Silakan restart aplikasi.', 'success')
    else:
        flash('Gagal restore database', 'danger')
    return redirect(url_for('settings.backup'))

@settings_bp.route('/holidays')
@login_required
def holidays():
    holidays = Holiday.query.order_by(Holiday.date).all()
    return render_template('settings/holidays.html', holidays=holidays)

@settings_bp.route('/holidays/add', methods=['POST'])
@login_required
def add_holiday():
    holiday = Holiday(
        name=request.form['name'],
        date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
        type=request.form.get('type', 'national')
    )
    db.session.add(holiday)
    db.session.commit()
    flash('Hari libur ditambahkan', 'success')
    return redirect(url_for('settings.holidays'))