from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')
student_bp = Blueprint('student', __name__, url_prefix='/student')
principal_bp = Blueprint('principal', __name__, url_prefix='/principal')
attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')
reports_bp = Blueprint('reports', __name__, url_prefix='/reports')
permissions_bp = Blueprint('permissions', __name__, url_prefix='/permissions')
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')