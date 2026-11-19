from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from . import principal_bp
from models import db, Student, Attendance, Classroom
from datetime import date

def principal_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'principal':
            flash('Akses ditolak. Hanya Kepala Sekolah yang bisa mengakses.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

@principal_bp.route('/dashboard')
@login_required
@principal_required
def dashboard():
    total_students = Student.query.filter_by(status='active').count()
    total_classes = Classroom.query.count()
    
    today = date.today()
    today_attendance = Attendance.query.filter_by(date=today).all()
    
    hadir = sum(1 for a in today_attendance if a.status == 'hadir')
    terlambat = sum(1 for a in today_attendance if a.status == 'terlambat')
    alfa = sum(1 for a in today_attendance if a.status == 'alfa')

    # Statistik per kelas
    class_stats = []
    for c in Classroom.query.all():
        students = c.students.all()
        present_count = sum(1 for s in students if Attendance.query.filter_by(student_id=s.id, date=today, status='hadir').first())
        class_stats.append({'name': c.full_name, 'total': len(students), 'present': present_count})

    return render_template('dashboard/principal.html',
        total_students=total_students, 
        total_classes=total_classes,
        hadir=hadir, terlambat=terlambat, alfa=alfa, 
        class_stats=class_stats, today=today)