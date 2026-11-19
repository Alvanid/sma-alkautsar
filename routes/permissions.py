from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import permissions_bp
from models import db, Permission, Student, User
from datetime import datetime

@permissions_bp.route('/')
@login_required
def index():
    if current_user.role == 'student':
        permissions = Permission.query.filter_by(student_id=current_user.student.id).order_by(Permission.created_at.desc()).all()
    else:
        permissions = Permission.query.order_by(Permission.created_at.desc()).all()
    return render_template('permissions/list.html', permissions=permissions)

@permissions_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if request.method == 'POST':
        student = current_user.student if current_user.role == 'student' else Student.query.get(request.form['student_id'])
        permission = Permission(
            student_id=student.id,
            type=request.form['type'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            reason=request.form['reason'],
            status='pending'
        )
        db.session.add(permission)
        db.session.commit()
        flash('Pengajuan berhasil dikirim', 'success')
        return redirect(url_for('permissions.index'))
    
    students = Student.query.filter_by(status='active').all() if current_user.role != 'student' else []
    return render_template('permissions/form.html', students=students, permission=None)

@permissions_bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    permission = Permission.query.get_or_404(id)
    permission.status = 'approved'
    permission.approved_by = current_user.id
    permission.notes = request.form.get('notes')
    db.session.commit()
    flash('Izin disetujui', 'success')
    return redirect(url_for('permissions.index'))

@permissions_bp.route('/<int:id>/reject', methods=['POST'])
@login_required
def reject(id):
    permission = Permission.query.get_or_404(id)
    permission.status = 'rejected'
    permission.approved_by = current_user.id
    permission.notes = request.form.get('notes')
    db.session.commit()
    flash('Izin ditolak', 'warning')
    return redirect(url_for('permissions.index'))