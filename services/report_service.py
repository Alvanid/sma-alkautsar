import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from datetime import datetime
from models import Student, Classroom, Attendance, AcademicYear

def export_attendance_excel(attendances, title="Laporan Absensi"):
    data = []
    for a in attendances:
        data.append({
            'Tanggal': a.date.strftime('%Y-%m-%d'),
            'NIS': a.student.nis,
            'Nama': a.student.full_name,
            'Kelas': a.student.classroom.full_name if a.student.classroom else '-',
            'Sesi': a.session.name,
            'Status': a.status.capitalize(),
            'Waktu': a.check_in_time.strftime('%H:%M:%S') if a.check_in_time else '-'
        })
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Absensi')
    output.seek(0)
    return output

def generate_pdf_report(attendances, school_logo_path, title="Laporan Absensi", period=""):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Header with logo
    if school_logo_path:
        try:
            logo = Image(school_logo_path, width=80, height=80)
            elements.append(logo)
        except:
            pass
    
    elements.append(Paragraph("SMA AL-KAUTSAR MANYAR", styles['Title']))
    elements.append(Paragraph("Manyar, Sekaran, Kabupaten Lamongan, Jawa Timur", styles['Normal']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(title, styles['Heading2']))
    elements.append(Paragraph(f"Periode: {period}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Table
    table_data = [['Tanggal', 'NIS', 'Nama', 'Kelas', 'Sesi', 'Status']]
    for a in attendances:
        table_data.append([
            a.date.strftime('%Y-%m-%d'),
            a.student.nis,
            a.student.full_name,
            a.student.classroom.full_name if a.student.classroom else '-',
            a.session.name,
            a.status.capitalize()
        ])
    
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#064E3B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 40))
    
    # Signature
    sig_data = [['', 'Lamongan, ' + datetime.now().strftime('%d %B %Y')],
                ['', ''],
                ['Kepala Sekolah', 'Petugas Absensi'],
                ['', ''],
                ['(___________________)', '(___________________)']]
    sig_table = Table(sig_data, colWidths=[200, 200])
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer