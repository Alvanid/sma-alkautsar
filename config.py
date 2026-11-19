import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'alkautsar-2026-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'attendance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SCHOOL_NAME = 'SMA AL-KAUTSAR MANYAR'
    SCHOOL_ADDRESS = 'Manyar, Sekaran, Kabupaten Lamongan, Jawa Timur'
    SCHOOL_LOGO = '/static/images/logo-alkautsar.png'
    BACKUP_FOLDER = os.path.join(BASE_DIR, 'instance', 'backups')
    TIMEZONE = 'Asia/Jakarta'