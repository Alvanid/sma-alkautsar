from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import student_bp
from models import db, Attendance, Permission
from services.qr_service import generate_qr_image
from services.attendance_service import calculate_attendance_percentage
from datetime import date

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.student:
        flash('Data siswa tidak ditemukan', 'warning')
        return redirect(url_for('auth.login'))
    
    student = current_user.student
    today = date.today()
    today_attendance = Attendance.query.filter_by(student_id=student.id, date=today).first()
    percentage = calculate_attendance_percentage(student.id)
    recent = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).limit(10).all()
    
    qr_image = None
    if student.qr_token:
        qr_image = generate_qr_image(student.qr_token, student.full_name, student.nis)
    
    return render_template('dashboard/student.html',
        student=student,
        today_attendance=today_attendance,
        percentage=percentage,
        recent=recent,
        qr_image=qr_image
    )

@student_bp.route('/profile')
@login_required
def profile():
    return render_template('students/profile.html', student=current_user.student)

@student_bp.route('/history')
@login_required
def history():
    attendances = Attendance.query.filter_by(student_id=current_user.student.id).order_by(Attendance.date.desc()).all()
    return render_template('students/history.html', attendances=attendances)