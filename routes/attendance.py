from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import attendance_bp
from models import db, Student, Attendance, AttendanceSession, User, Classroom
from services.attendance_service import record_attendance, check_late
from datetime import datetime, date

@attendance_bp.route('/scan', methods=['GET'])
@login_required
def scan_page():
    sessions = AttendanceSession.query.filter_by(is_active=True).all()
    return render_template('attendance/scan.html', sessions=sessions)

@attendance_bp.route('/scan/process', methods=['POST'])
@login_required
def scan_process():
    """Process QR Code scan"""
    token = request.form.get('token')
    session_id = request.form.get('session_id', type=int)
    
    if not token or not session_id:
        return jsonify({'success': False, 'message': 'Data tidak lengkap'})
    
    # Find student by QR token
    student = Student.query.filter_by(qr_token=token, status='active').first()
    if not student:
        return jsonify({'success': False, 'message': 'QR Code tidak valid'})
    
    # Check if already scanned
    existing = Attendance.query.filter_by(
        student_id=student.id, session_id=session_id, date=date.today()
    ).first()
    if existing:
        return jsonify({
            'success': False, 
            'message': f'{student.full_name} sudah absen untuk sesi ini',
            'student': student.full_name
        })
    
    # Determine status
    now = datetime.now()
    session = AttendanceSession.query.get(session_id)
    status = 'hadir'
    if session and session.late_threshold and now.time() > session.late_threshold:
        status = 'terlambat'
    
    result = record_attendance(
        student_id=student.id,
        session_id=session_id,
        status=status,
        recorded_by=current_user.id
    )
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': f'Absensi {student.full_name} berhasil ({status})',
            'student': student.full_name,
            'nis': student.nis,
            'status': status,
            'time': now.strftime('%H:%M:%S')
        })
    else:
        return jsonify({'success': False, 'message': result['message']})

@attendance_bp.route('/manual', methods=['GET', 'POST'])
@login_required
def manual():
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        session_id = request.form.get('session_id', type=int)
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        result = record_attendance(
            student_id=student_id,
            session_id=session_id,
            status=status,
            recorded_by=current_user.id,
            notes=notes
        )
        
        if result['success']:
            flash('Absensi manual berhasil dicatat', 'success')
        else:
            flash(result['message'], 'danger')
        return redirect(url_for('attendance.manual'))
    
    students = Student.query.filter_by(status='active').all()
    sessions = AttendanceSession.query.filter_by(is_active=True).all()
    return render_template('attendance/manual.html', students=students, sessions=sessions)

@attendance_bp.route('/data')
@login_required
def data():
    date_filter = request.args.get('date', date.today().isoformat())
    class_id = request.args.get('class_id', type=int)
    
    query = Attendance.query.filter_by(date=date_filter)
    if class_id:
        student_ids = [s.id for s in Student.query.filter_by(class_id=class_id).all()]
        query = query.filter(Attendance.student_id.in_(student_ids))
    
    attendances = query.all()
    
    # FIX: Query Classroom directly instead of complex join
    classes = Classroom.query.all()
    
    return render_template('attendance/data.html', 
        attendances=attendances, 
        date_filter=date_filter,
        class_id=class_id,
        classes=classes)

@attendance_bp.route('/sessions')
@login_required
def sessions():
    sessions = AttendanceSession.query.all()
    return render_template('attendance/sessions.html', sessions=sessions)

@attendance_bp.route('/sessions/add', methods=['POST'])
@login_required
def add_session():
    session = AttendanceSession(
        name=request.form['name'],
        start_time=datetime.strptime(request.form['start_time'], '%H:%M').time(),
        end_time=datetime.strptime(request.form['end_time'], '%H:%M').time(),
        late_threshold=datetime.strptime(request.form['late_threshold'], '%H:%M').time() if request.form.get('late_threshold') else None,
        is_active=True
    )
    db.session.add(session)
    db.session.commit()
    flash('Sesi absensi ditambahkan', 'success')
    return redirect(url_for('attendance.sessions'))