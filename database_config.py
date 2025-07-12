# Database Configuration for Clothing Swap Platform
import os

class DatabaseConfig:
    """SQLite database configuration and optimization settings"""
    
    # Database file location
    DB_NAME = 'clothing_swap.db'
    DB_DIR = 'instance'
    DB_PATH = os.path.join(DB_DIR, DB_NAME)
    
    # SQLite optimization settings
    SQLITE_PRAGMAS = {
        'foreign_keys': 'ON',           # Enable foreign key constraints
        'journal_mode': 'WAL',          # Write-Ahead Logging for better concurrency
        'synchronous': 'NORMAL',        # Balance between safety and performance
        'cache_size': 10000,            # Increase cache size (10MB)
        'temp_store': 'MEMORY',         # Store temporary tables in memory
        'mmap_size': 268435456,         # Use memory-mapped I/O (256MB)
        'page_size': 4096,              # Optimal page size for most systems
        'auto_vacuum': 'INCREMENTAL'    # Automatic database maintenance
    }
    
    # Connection pool settings
    POOL_SIZE = 20
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600  # 1 hour
    
    # File upload settings
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Performance monitoring
    ENABLE_QUERY_LOGGING = False
    SLOW_QUERY_THRESHOLD = 1.0  # seconds
    
    @classmethod
    def get_database_uri(cls):
        """Get the complete database URI"""
        return f'sqlite:///{cls.DB_PATH}'
    
    @classmethod
    def get_engine_options(cls):
        """Get SQLAlchemy engine options"""
        return {
            'pool_pre_ping': True,
            'pool_recycle': cls.POOL_RECYCLE,
            'pool_timeout': cls.POOL_TIMEOUT,
            'connect_args': {
                'check_same_thread': False,
                'timeout': 20
            }
        }
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        os.makedirs(cls.DB_DIR, exist_ok=True)
        os.makedirs('static/uploads', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

# Database maintenance schedule
MAINTENANCE_TASKS = {
    'analyze': 'daily',      # Update query planner statistics
    'vacuum': 'weekly',      # Reclaim space and defragment
    'integrity_check': 'weekly',  # Check database integrity
    'backup': 'daily'        # Create database backups
}

# Backup settings
BACKUP_DIR = 'backups'
BACKUP_RETENTION_DAYS = 30
MAX_BACKUPS = 10
