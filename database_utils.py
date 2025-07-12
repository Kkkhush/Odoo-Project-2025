"""
Database utilities for the Clothing Swap Platform
Provides database maintenance, backup, and optimization functions
"""
import os
import shutil
import sqlite3
import logging
from datetime import datetime, timedelta
from database_config import DatabaseConfig, BACKUP_DIR, BACKUP_RETENTION_DAYS, MAX_BACKUPS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations, maintenance, and backups"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or DatabaseConfig.DB_PATH
        self.backup_dir = BACKUP_DIR
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def get_connection(self):
        """Get optimized SQLite connection"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Apply optimization pragmas
            cursor = conn.cursor()
            for pragma, value in DatabaseConfig.SQLITE_PRAGMAS.items():
                cursor.execute(f"PRAGMA {pragma}={value}")
            
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_backup(self):
        """Create a backup of the database"""
        try:
            if not os.path.exists(self.db_path):
                logger.warning("Database file does not exist, skipping backup")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"clothing_swap_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create backup using SQLite backup API
            source = sqlite3.connect(self.db_path)
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            backup.close()
            source.close()
            
            logger.info(f"Database backup created: {backup_path}")
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def restore_backup(self, backup_path):
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create backup of current database before restore
            self.create_backup()
            
            # Copy backup to main database location
            shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def vacuum_database(self):
        """Vacuum database to reclaim space and optimize"""
        try:
            with self.get_connection() as conn:
                conn.execute("VACUUM")
                conn.commit()
            logger.info("Database vacuum completed")
            return True
        except Exception as e:
            logger.error(f"Database vacuum failed: {e}")
            return False
    
    def analyze_database(self):
        """Update database statistics for query optimization"""
        try:
            with self.get_connection() as conn:
                conn.execute("ANALYZE")
                conn.commit()
            logger.info("Database analysis completed")
            return True
        except Exception as e:
            logger.error(f"Database analysis failed: {e}")
            return False
    
    def check_integrity(self):
        """Check database integrity"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result and result[0] == 'ok':
                    logger.info("Database integrity check passed")
                    return True
                else:
                    logger.error(f"Database integrity check failed: {result}")
                    return False
        except Exception as e:
            logger.error(f"Database integrity check error: {e}")
            return False
    
    def get_database_info(self):
        """Get database information and statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get database size
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                db_size = page_count * page_size
                
                # Get table information
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Get row counts for each table
                table_stats = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_stats[table] = count
                
                return {
                    'size_bytes': db_size,
                    'size_mb': round(db_size / (1024 * 1024), 2),
                    'page_count': page_count,
                    'page_size': page_size,
                    'tables': table_stats,
                    'total_records': sum(table_stats.values())
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return None
    
    def optimize_database(self):
        """Run full database optimization"""
        logger.info("Starting database optimization...")
        
        success = True
        success &= self.analyze_database()
        success &= self.vacuum_database()
        success &= self.check_integrity()
        
        if success:
            logger.info("Database optimization completed successfully")
        else:
            logger.error("Database optimization completed with errors")
        
        return success
    
    def _cleanup_old_backups(self):
        """Remove old backup files"""
        try:
            if not os.path.exists(self.backup_dir):
                return
            
            # Get all backup files
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('clothing_swap_backup_') and filename.endswith('.db'):
                    filepath = os.path.join(self.backup_dir, filename)
                    backups.append((filepath, os.path.getmtime(filepath)))
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Remove excess backups (keep only MAX_BACKUPS)
            if len(backups) > MAX_BACKUPS:
                for filepath, _ in backups[MAX_BACKUPS:]:
                    os.remove(filepath)
                    logger.info(f"Removed old backup: {filepath}")
            
            # Remove backups older than retention period
            cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
            cutoff_timestamp = cutoff_date.timestamp()
            
            for filepath, mtime in backups:
                if mtime < cutoff_timestamp:
                    os.remove(filepath)
                    logger.info(f"Removed expired backup: {filepath}")
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")

# Convenience functions
def create_backup():
    """Create a database backup"""
    manager = DatabaseManager()
    return manager.create_backup()

def optimize_database():
    """Optimize the database"""
    manager = DatabaseManager()
    return manager.optimize_database()

def get_database_info():
    """Get database information"""
    manager = DatabaseManager()
    return manager.get_database_info()

def check_database_health():
    """Perform a complete database health check"""
    manager = DatabaseManager()
    
    print("=== Database Health Check ===")
    
    # Check integrity
    integrity_ok = manager.check_integrity()
    print(f"Integrity Check: {'PASS' if integrity_ok else 'FAIL'}")
    
    # Get database info
    info = manager.get_database_info()
    if info:
        print(f"Database Size: {info['size_mb']} MB")
        print(f"Total Records: {info['total_records']}")
        print("Table Statistics:")
        for table, count in info['tables'].items():
            print(f"  {table}: {count} records")
    
    # Create backup
    backup_path = manager.create_backup()
    print(f"Backup Created: {'YES' if backup_path else 'NO'}")
    
    print("=============================")
    
    return integrity_ok and info is not None

if __name__ == "__main__":
    # Run database health check when executed directly
    check_database_health()
