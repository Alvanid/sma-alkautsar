from datetime import datetime, date, time
from models import db, Attendance, AttendanceSession, Student, Permission

def record_attendance(student_id, session_id, status='hadir', recorded_by=None, notes=None):
    today = date.today()
    existing = Attendance.query.filter_by(
        student_id=student_id, session_id=session_id, date=today
    ).first()
    
    if existing:
        return {'success': False, 'message': 'Absensi sudah tercatat untuk sesi ini'}
    
    now = datetime.now()
    attendance = Attendance(
        student_id=student_id,
        session_id=session_id,
        date=today,
        status=status,
        check_in_time=now if session_id == 1 else None,
        check_out_time=now if session_id == 2 else None,
        notes=notes,
        recorded_by=recorded_by
    )
    db.session.add(attendance)
    db.session.commit()
    return {'success': True, 'attendance': attendance}

def check_late(session_id, check_time):
    """Check if student is late based on session threshold"""
    session = AttendanceSession.query.get(session_id)
    if not session or not session.late_threshold:
        return False
    return check_time.time() > session.late_threshold

def get_student_status(student_id, date=None):
    if not date:
        date = date.today()
    attendances = Attendance.query.filter_by(student_id=student_id, date=date).all()
    statuses = {a.session_id: a.status for a in attendances}
    return statuses

def calculate_attendance_percentage(student_id, academic_year_id=None):
    total_days = Attendance.query.filter_by(student_id=student_id).count()
    if total_days == 0:
        return 0
    present = Attendance.query.filter_by(student_id=student_id, status='hadir').count()
    return round((present / total_days) * 100, 2)