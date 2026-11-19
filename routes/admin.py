from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from . import admin_bp
from models import db, User, Student, Teacher, Classroom, AcademicYear, Attendance, AuditLog, SystemSetting
from services.qr_service import generate_qr_image
from datetime import date, datetime

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Akses ditolak', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_students = Student.query.filter_by(status='active').count()
    total_teachers = Teacher.query.filter_by(is_active=True).count()
    total_classes = Classroom.query.count()
    
    today = date.today()
    today_attendance = Attendance.query.filter_by(date=today).all()
    
    hadir = sum(1 for a in today_attendance if a.status == 'hadir')
    terlambat = sum(1 for a in today_attendance if a.status == 'terlambat')
    izin = sum(1 for a in today_attendance if a.status == 'izin')
    sakit = sum(1 for a in today_attendance if a.status == 'sakit')
    alfa = sum(1 for a in today_attendance if a.status == 'alfa')
    
    recent_activity = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    late_students = Attendance.query.filter_by(date=today, status='terlambat').all()
    
    return render_template('dashboard/admin.html',
        total_students=total_students,
        total_teachers=total_teachers,
        total_classes=total_classes,
        hadir=hadir, terlambat=terlambat, izin=izin, sakit=sakit, alfa=alfa,
        recent_activity=recent_activity,
        late_students=late_students
    )

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    class_id = request.args.get('class_id', '', type=int)
    
    query = Student.query.filter_by(status='active')
    if search:
        query = query.filter(Student.full_name.ilike(f'%{search}%') | Student.nis.ilike(f'%{search}%'))
    if class_id:
        query = query.filter_by(class_id=class_id)
    
    students = query.paginate(page=page, per_page=20)
    classes = Classroom.query.all()
    
    return render_template('students/list.html', students=students, classes=classes, search=search, class_id=class_id)

@admin_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    if request.method == 'POST':
        student = Student(
            nis=request.form['nis'],
            nisn=request.form.get('nisn'),
            full_name=request.form['full_name'],
            gender=request.form['gender'],
            birth_place=request.form.get('birth_place'),
            birth_date=datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date() if request.form.get('birth_date') else None,
            address=request.form.get('address'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            parent_name=request.form.get('parent_name'),
            parent_phone=request.form.get('parent_phone'),
            class_id=request.form.get('class_id', type=int),
            year_entry=request.form.get('year_entry', type=int),
            status='active'
        )
        student.generate_qr_token()
        
        # Create user account
        user = User(
            username=student.nis,
            full_name=student.full_name,
            role='student',
            email=student.email
        )
        user.set_password('siswa123')
        db.session.add(user)
        db.session.flush()
        student.user_id = user.id
        
        db.session.add(student)
        db.session.commit()
        
        flash('Siswa berhasil ditambahkan', 'success')
        return redirect(url_for('admin.students'))
    
    classes = Classroom.query.all()
    return render_template('students/form.html', student=None, classes=classes)

@admin_bp.route('/students/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.nis = request.form['nis']
        student.full_name = request.form['full_name']
        student.gender = request.form['gender']
        student.class_id = request.form.get('class_id', type=int)
        student.phone = request.form.get('phone')
        student.address = request.form.get('address')
        db.session.commit()
        flash('Data siswa diperbarui', 'success')
        return redirect(url_for('admin.students'))
    
    classes = Classroom.query.all()
    return render_template('students/form.html', student=student, classes=classes)

@admin_bp.route('/students/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    student.status = 'inactive'
    db.session.commit()
    flash('Siswa dinonaktifkan', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/teachers')
@login_required
@admin_required
def teachers():
    teachers = Teacher.query.all()
    return render_template('teachers/list.html', teachers=teachers)

@admin_bp.route('/teachers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_teacher():
    if request.method == 'POST':
        teacher = Teacher(
            nip=request.form.get('nip'),
            full_name=request.form['full_name'],
            gender=request.form['gender'],
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            is_active=True
        )
        user = User(
            username=request.form.get('nip') or request.form['full_name'].lower().replace(' ', '_'),
            full_name=teacher.full_name,
            role='teacher',
            email=teacher.email
        )
        user.set_password('guru123')
        db.session.add(user)
        db.session.flush()
        teacher.user_id = user.id
        
        db.session.add(teacher)
        db.session.commit()
        flash('Guru berhasil ditambahkan', 'success')
        return redirect(url_for('admin.teachers'))
    
    return render_template('teachers/form.html', teacher=None)

@admin_bp.route('/classrooms')
@login_required
@admin_required
def classrooms():
    classes = Classroom.query.all()
    return render_template('classrooms/list.html', classes=classes)

@admin_bp.route('/classrooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_classroom():
    if request.method == 'POST':
        active_year = AcademicYear.query.filter_by(is_active=True).first()
        classroom = Classroom(
            grade=request.form['grade'],
            name=request.form['name'],
            full_name=f"{request.form['grade']}-{request.form['name']}",
            academic_year_id=active_year.id if active_year else 1,
            homeroom_teacher_id=request.form.get('homeroom_teacher_id', type=int)
        )
        db.session.add(classroom)
        db.session.commit()
        flash('Kelas berhasil ditambahkan', 'success')
        return redirect(url_for('admin.classrooms'))
    
    teachers = Teacher.query.all()
    return render_template('classrooms/form.html', classroom=None, teachers=teachers)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('settings/users.html', users=users)

@admin_bp.route('/audit-log')
@login_required
@admin_required
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return render_template('settings/audit_log.html', logs=logs)

@admin_bp.route('/qr/<int:student_id>')
@login_required
@admin_required
def student_qr(student_id):
    student = Student.query.get_or_404(student_id)
    if not student.qr_token:
        student.generate_qr_token()
        db.session.commit()
    qr_image = generate_qr_image(student.qr_token, student.full_name, student.nis)
    return render_template('students/qr.html', student=student, qr_image=qr_image)