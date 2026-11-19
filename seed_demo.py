from app import create_app
from models import db, User, Student, Teacher, Classroom, AcademicYear
import uuid

def seed_demo():
    app = create_app()
    with app.app_context():
        db.create_all()

        year = AcademicYear.query.filter_by(is_active=True).first()
        if not year:
            from datetime import date
            year = AcademicYear(year='2025/2026', start_date=date(2025,7,1),
                                end_date=date(2026,6,30), is_active=True, semester=1)
            db.session.add(year); db.session.commit()

        # --- Guru contoh (walikelas) ---
        teachers_data = [
            ('198501012010011001', 'AHMAD FAUZI, S.Pd', 'L', 'Matematika'),
            ('198702022011022002', 'SITI NURHALIZA, S.Pd', 'P', 'Bahasa Indonesia'),
            ('199003032015031003', 'BUDI SANTOSO, M.Pd', 'L', 'IPA'),
        ]
        teacher_objs = {}
        for nip, name, g, subj in teachers_data:
            if not Teacher.query.filter_by(nip=nip).first():
                t = Teacher(nip=nip, full_name=name, gender=g, subject=subj, is_active=True)
                db.session.add(t); db.session.flush()
                teacher_objs[name] = t
                # akun guru
                u = User(username=nip, full_name=name, role='teacher', email=None)
                u.set_password('guru123')
                db.session.add(u); db.session.flush()
                t.user_id = u.id
        db.session.commit()

        # --- Kelas contoh ---
        classes_data = [
            ('X', '1', 'AHMAD FAUZI, S.Pd'),
            ('XI', '1', 'SITI NURHALIZA, S.Pd'),
            ('XII', '1', 'BUDI SANTOSO, M.Pd'),
        ]
        for grade, name, wali in classes_data:
            if not Classroom.query.filter_by(grade=grade, name=name, academic_year_id=year.id).first():
                c = Classroom(grade=grade, name=name, full_name=f'{grade}-{name}',
                              academic_year_id=year.id,
                              homeroom_teacher_id=teacher_objs[wali].id)
                db.session.add(c)
        db.session.commit()

        # --- Siswa contoh ---
        students_data = [
            ('2025001', '20251001', 'ALVAN GHOFFAR', 'L', 'X', '1'),
            ('2025002', '20251002', 'NUR AINI', 'P', 'X', '1'),
            ('2025003', '20251003', 'FAIZAL RAHMAN', 'L', 'XI', '1'),
            ('2025004', '20251004', 'DEWI LESTARI', 'P', 'XI', '1'),
            ('2025005', '20251005', 'RIKI PRASETYO', 'L', 'XII', '1'),
        ]
        for nis, nisn, name, g, grade, cname in students_data:
            if Student.query.filter_by(nis=nis).first():
                continue
            cls = Classroom.query.filter_by(grade=grade, name=cname).first()
            s = Student(nis=nis, nisn=nisn, full_name=name, gender=g,
                        birth_place='Lamongan', year_entry=2025, status='active',
                        class_id=cls.id if cls else None)
            s.generate_qr_token()
            u = User(username=nis, full_name=name, role='student')
            u.set_password('siswa123')
            db.session.add(u); db.session.flush()
            s.user_id = u.id
            db.session.add(s)
        db.session.commit()

        print('🎉 Demo data dibuat:')
        print('   Kelas   : X-1, XI-1, XII-1')
        print('   Guru    : 3 orang (login pakai NIP / guru123)')
        print('   Siswa   : 5 orang (login pakai NIS / siswa123)')
        print('   QR      : sudah di-generate otomatis untuk tiap siswa')

if __name__ == '__main__':
    seed_demo()