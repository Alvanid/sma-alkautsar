from app import create_app
from models import db, User, Student, Teacher, Classroom, AcademicYear, AttendanceSession, SystemSetting
from datetime import date, time, datetime

def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create admin
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@alkautsar.sch.id',
                full_name='Administrator',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✓ Admin created: admin / admin123')
        
        # Create principal
        if not User.query.filter_by(username='kepsek').first():
            principal = User(
                username='kepsek',
                email='kepsek@alkautsar.sch.id',
                full_name='Kepala Sekolah',
                role='principal'
            )
            principal.set_password('kepsek123')
            db.session.add(principal)
            db.session.commit()
            print('✓ Principal created: kepsek / kepsek123')
        
        # Academic Year
        if not AcademicYear.query.first():
            year = AcademicYear(
                year='2025/2026',
                start_date=date(2025, 7, 1),
                end_date=date(2026, 6, 30),
                is_active=True,
                semester=1
            )
            db.session.add(year)
            db.session.commit()
            print('✓ Academic Year created')
        
        # Attendance Sessions
        if not AttendanceSession.query.first():
            masuk = AttendanceSession(
                name='Masuk',
                start_time=time(6, 30),
                end_time=time(7, 30),
                late_threshold=time(7, 15),
                is_active=True
            )
            pulang = AttendanceSession(
                name='Pulang',
                start_time=time(14, 0),
                end_time=time(15, 0),
                is_active=True
            )
            db.session.add_all([masuk, pulang])
            db.session.commit()
            print('✓ Attendance Sessions created')
        
        # System Settings
        settings_data = [
            ('school_name', 'SMA AL-KAUTSAR MANYAR', 'Nama sekolah'),
            ('school_address', 'Manyar, Sekaran, Kabupaten Lamongan, Jawa Timur', 'Alamat'),
            ('entry_time', '07:00', 'Jam masuk'),
            ('exit_time', '14:00', 'Jam pulang'),
            ('late_threshold', '07:15', 'Batas keterlambatan'),
            ('whatsapp_gateway', '', 'API WhatsApp Gateway'),
        ]
        for key, value, desc in settings_data:
            if not SystemSetting.query.filter_by(key=key).first():
                db.session.add(SystemSetting(key=key, value=value, description=desc))
        db.session.commit()
        print('✓ System settings created')
        
        print('\n🎉 Seeding completed!')
        print('\nAkun yang tersedia:')
        print('  Admin    : admin / admin123')
        print('  Kepala   : kepsek / kepsek123')

if __name__ == '__main__':
    seed()