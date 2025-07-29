from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import settings
import logging

# 配置日志
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 检查是否为PostgreSQL连接
is_postgresql = settings.database_url.startswith('postgresql')

if is_postgresql:
    # PostgreSQL优化配置
    engine = create_engine(
        settings.database_url,
        # 连接池配置
        poolclass=QueuePool,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        pool_pre_ping=settings.db_pool_pre_ping,
        
        # PostgreSQL特定优化
        connect_args={
            "options": "-c timezone=utc",
            "application_name": "Ghibli AI Backend",
        },
        
        # 性能优化
        echo=False,  # 生产环境关闭SQL日志
        future=True,
    )
    
    # PostgreSQL连接优化设置
    @event.listens_for(engine, "connect")
    def set_postgresql_pragma(dbapi_connection, connection_record):
        """PostgreSQL连接优化设置"""
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SET statement_timeout = '30s'")
            cursor.execute("SET lock_timeout = '10s'")
            cursor.close()
        except Exception as e:
            logging.warning(f"PostgreSQL连接设置失败: {e}")
else:
    # SQLite配置（保持兼容性）
    engine = create_engine(
        settings.database_url, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # 避免会话过期问题
)

Base = declarative_base()

def get_db():
    """数据库会话依赖注入"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def create_tables():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)

def check_db_connection():
    """检查数据库连接健康状态"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logging.error(f"数据库连接失败: {e}")
        return False
