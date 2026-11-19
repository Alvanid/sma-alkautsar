import os
import shutil
from datetime import datetime
from models import db, Backup

def create_backup(user_id, db_path, backup_folder):
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_{timestamp}.db"
    filepath = os.path.join(backup_folder, filename)
    
    shutil.copy2(db_path, filepath)
    
    size = os.path.getsize(filepath)
    backup = Backup(
        filename=filename,
        size=size,
        created_by=user_id
    )
    db.session.add(backup)
    db.session.commit()
    return backup

def restore_backup(backup_id, db_path, backup_folder):
    backup = Backup.query.get(backup_id)
    if not backup:
        return False
    
    source = os.path.join(backup_folder, backup.filename)
    if os.path.exists(source):
        shutil.copy2(source, db_path)
        return True
    return False