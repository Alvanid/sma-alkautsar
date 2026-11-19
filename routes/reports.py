from flask import render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from . import reports_bp
from models import db, Attendance, Student, Classroom, AttendanceSession
from services.report_service import export_attendance_excel, generate_pdf_report
from datetime import datetime, date

@reports_bp.route('/')
@login_required
def index():
    today = date.today().isoformat()
    return render_template('reports/index.html', today=today)

@reports_bp.route('/daily')
@login_required
def daily():
    date_filter = request.args.get('date', date.today().isoformat())
    attendances = Attendance.query.filter_by(date=date_filter).all()
    return render_template('reports/daily.html', attendances=attendances, date_filter=date_filter)

@reports_bp.route('/monthly')
@login_required
def monthly():
    month = request.args.get('month', date.today().strftime('%Y-%m'))
    try:
        start = datetime.strptime(month + '-01', '%Y-%m-%d').date()
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1)
        else:
            end = start.replace(month=start.month + 1, day=1)
    except ValueError:
        start = date.today().replace(day=1)
        end = (start.replace(month=start.month % 12 + 1) if start.month < 12 else start.replace(year=start.year + 1, month=1))
    
    attendances = Attendance.query.filter(
        Attendance.date >= start,
        Attendance.date < end
    ).all()
    return render_template('reports/monthly.html', attendances=attendances, month=month)

@reports_bp.route('/export/excel')
@login_required
def export_excel():
    date_from = request.args.get('from', date.today().isoformat())
    date_to = request.args.get('to', date.today().isoformat())
    attendances = Attendance.query.filter(
        Attendance.date >= date_from,
        Attendance.date <= date_to
    ).all()
    
    output = export_attendance_excel(attendances, f"Laporan {date_from} - {date_to}")
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'absensi_{date_from}_{date_to}.xlsx'
    )

@reports_bp.route('/export/pdf')
@login_required
def export_pdf():
    date_from = request.args.get('from', date.today().isoformat())
    date_to = request.args.get('to', date.today().isoformat())
    attendances = Attendance.query.filter(
        Attendance.date >= date_from,
        Attendance.date <= date_to
    ).all()
    
    output = generate_pdf_report(
        attendances, 
        'static/images/logo-alkautsar.png',
        "Laporan Absensi",
        f"{date_from} - {date_to}"
    )
    return send_file(
        output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'absensi_{date_from}_{date_to}.pdf'
    )