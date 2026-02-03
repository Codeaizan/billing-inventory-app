import os
import shutil
from datetime import datetime
from typing import Tuple, List, Optional
from database.db_manager import db
from config import BACKUP_DIR
from utils.logger import logger

class BackupManager:
    """Manages database backup and restore"""
    
    def create_backup(self, backup_name: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create database backup
        Returns: (success, message, backup_path)
        """
        try:
            # Generate backup filename
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"backup_{timestamp}.db"
            
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            
            # Create backup
            success = db.backup_database(backup_path)
            
            if success:
                return True, f"Backup created successfully", backup_path
            else:
                return False, "Failed to create backup", None
                
        except Exception as e:
            logger.error(f"Backup error: {e}")
            return False, f"Backup error: {str(e)}", None
    
    def restore_backup(self, backup_path: str) -> Tuple[bool, str]:
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                return False, "Backup file not found"
            
            success = db.restore_database(backup_path)
            
            if success:
                return True, "Database restored successfully"
            else:
                return False, "Failed to restore database"
                
        except Exception as e:
            logger.error(f"Restore error: {e}")
            return False, f"Restore error: {str(e)}"
    
    def list_backups(self) -> List[dict]:
        """List all available backups"""
        try:
            backups = []
            
            if not os.path.exists(BACKUP_DIR):
                return backups
            
            for filename in os.listdir(BACKUP_DIR):
                if filename.endswith('.db'):
                    filepath = os.path.join(BACKUP_DIR, filename)
                    file_size = os.path.getsize(filepath)
                    file_time = os.path.getmtime(filepath)
                    
                    backups.append({
                        'name': filename,
                        'path': filepath,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'created_at': datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def delete_backup(self, backup_path: str) -> Tuple[bool, str]:
        """Delete a backup file"""
        try:
            if not os.path.exists(backup_path):
                return False, "Backup file not found"
            
            os.remove(backup_path)
            logger.info(f"Backup deleted: {backup_path}")
            return True, "Backup deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting backup: {e}")
            return False, f"Error deleting backup: {str(e)}"
    
    def auto_backup(self) -> Tuple[bool, str]:
        """Create automatic backup"""
        backup_name = f"auto_backup_{datetime.now().strftime('%Y%m%d')}.db"
        return self.create_backup(backup_name)

# Create global instance
backup_manager = BackupManager()
