from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import teacher_bp
from models import db, Student, Attendance, Classroom

@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.teacher:
        flash('Data guru tidak ditemukan', 'warning')
        return redirect(url_for('auth.login'))
    
    teacher = current_user.teacher
    classes = teacher.classrooms
    return render_template('dashboard/teacher.html', teacher=teacher, classes=classes)

@teacher_bp.route('/class/<int:class_id>')
@login_required
def class_detail(class_id):
    classroom = Classroom.query.get_or_404(class_id)
    students = classroom.students.all()
    return render_template('classrooms/detail.html', classroom=classroom, students=students)