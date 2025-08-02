"""
Redis客户端工具类

这个模块提供Redis连接和常用操作的封装
专门为AI图片处理项目优化的缓存功能
"""

import json
import redis
from typing import Optional, Dict, Any, Union
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis客户端管理类"""
    
    def __init__(self):
        """初始化Redis连接"""
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """建立Redis连接"""
        try:
            # 解析Redis URL
            if settings.redis_url.startswith('redis://'):
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    max_connections=settings.redis_max_connections,
                    decode_responses=True,  # 自动解码字符串
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            else:
                # 直接连接
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=settings.redis_db,
                    password=settings.redis_password if settings.redis_password else None,
                    max_connections=settings.redis_max_connections,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            
            # 测试连接
            self.redis_client.ping()
            logger.info("✅ Redis连接成功")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis连接失败: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """检查Redis是否连接正常"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置键值对
        
        Args:
            key: 键名
            value: 值（自动JSON序列化）
            expire: 过期时间（秒）
        
        Returns:
            是否设置成功
        """
        if not self.is_connected():
            logger.warning("Redis未连接，跳过缓存操作")
            return False
        
        try:
            # 如果是字典或列表，自动JSON序列化
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = self.redis_client.set(key, value, ex=expire)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis设置失败 {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取值
        
        Args:
            key: 键名
        
        Returns:
            值（自动JSON反序列化）
        """
        if not self.is_connected():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # 如果不是JSON，直接返回字符串
                return value
        except Exception as e:
            logger.error(f"Redis获取失败 {key}: {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """删除键"""
        if not self.is_connected():
            return 0
        
        try:
            return self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis删除失败 {keys}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis检查存在失败 {key}: {e}")
            return False
    
    def hset(self, name: str, mapping: Dict[str, Any], expire: Optional[int] = None) -> bool:
        """
        设置哈希表
        
        Args:
            name: 哈希表名
            mapping: 字段映射
            expire: 过期时间（秒）
        
        Returns:
            是否设置成功
        """
        if not self.is_connected():
            return False
        
        try:
            # 序列化所有值
            serialized_mapping = {}
            for key, value in mapping.items():
                if isinstance(value, (dict, list)):
                    serialized_mapping[key] = json.dumps(value, ensure_ascii=False)
                else:
                    serialized_mapping[key] = str(value)
            
            result = self.redis_client.hset(name, mapping=serialized_mapping)
            
            # 设置过期时间
            if expire:
                self.redis_client.expire(name, expire)
            
            return True
        except Exception as e:
            logger.error(f"Redis哈希设置失败 {name}: {e}")
            return False
    
    def hget(self, name: str, key: str) -> Optional[Any]:
        """获取哈希表字段值"""
        if not self.is_connected():
            return None
        
        try:
            value = self.redis_client.hget(name, key)
            if value is None:
                return None
            
            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis哈希获取失败 {name}.{key}: {e}")
            return None
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """获取整个哈希表"""
        if not self.is_connected():
            return {}
        
        try:
            data = self.redis_client.hgetall(name)
            if not data:
                return {}
            
            # 反序列化所有值
            result = {}
            for key, value in data.items():
                try:
                    result[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[key] = value
            
            return result
        except Exception as e:
            logger.error(f"Redis哈希获取全部失败 {name}: {e}")
            return {}
    
    def hdel(self, name: str, *keys: str) -> int:
        """删除哈希表字段"""
        if not self.is_connected():
            return 0
        
        try:
            return self.redis_client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Redis哈希删除失败 {name}.{keys}: {e}")
            return 0

# 全局Redis客户端实例
redis_client = RedisClient()

# 任务进度管理器
class TaskProgressManager:
    """任务进度管理器 - 使用Redis替代内存字典"""
    
    @staticmethod
    def set_progress(task_id: str, progress_data: Dict[str, Any], expire: int = 600) -> bool:
        """
        设置任务进度
        
        Args:
            task_id: 任务ID
            progress_data: 进度数据
            expire: 过期时间（秒，默认10分钟）
        
        Returns:
            是否设置成功
        """
        key = f"task_progress:{task_id}"
        return redis_client.hset(key, progress_data, expire)
    
    @staticmethod
    def get_progress(task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务进度"""
        key = f"task_progress:{task_id}"
        return redis_client.hgetall(key)
    
    @staticmethod
    def update_progress(task_id: str, updates: Dict[str, Any]) -> bool:
        """更新任务进度"""
        key = f"task_progress:{task_id}"
        existing = redis_client.hgetall(key)
        if existing:
            existing.update(updates)
            return redis_client.hset(key, existing, expire=600)
        return False
    
    @staticmethod
    def delete_progress(task_id: str) -> bool:
        """删除任务进度"""
        key = f"task_progress:{task_id}"
        return bool(redis_client.delete(key))
    
    @staticmethod
    def exists(task_id: str) -> bool:
        """检查任务是否存在"""
        key = f"task_progress:{task_id}"
        return redis_client.exists(key)

# 用户缓存管理器
class UserCacheManager:
    """用户缓存管理器"""
    
    @staticmethod
    def cache_user(user_id: int, user_data: Dict[str, Any], expire: int = 3600) -> bool:
        """
        缓存用户信息
        
        Args:
            user_id: 用户ID
            user_data: 用户数据
            expire: 过期时间（秒，默认1小时）
        """
        key = f"user:{user_id}"
        return redis_client.set(key, user_data, expire)
    
    @staticmethod
    def get_user(user_id: int) -> Optional[Dict[str, Any]]:
        """获取缓存的用户信息"""
        key = f"user:{user_id}"
        return redis_client.get(key)
    
    @staticmethod
    def cache_user_by_token(token: str, user_data: Dict[str, Any], expire: int = 1800) -> bool:
        """
        根据token缓存用户信息
        
        Args:
            token: 访问令牌
            user_data: 用户数据  
            expire: 过期时间（秒，默认30分钟）
        """
        key = f"token:{token}"
        return redis_client.set(key, user_data, expire)
    
    @staticmethod
    def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
        """根据token获取用户信息"""
        key = f"token:{token}"
        return redis_client.get(key)
    
    @staticmethod
    def delete_user_cache(user_id: int) -> bool:
        """删除用户缓存"""
        key = f"user:{user_id}"
        return bool(redis_client.delete(key))
    
    @staticmethod
    def delete_token_cache(token: str) -> bool:
        """删除token缓存"""
        key = f"token:{token}"
        return bool(redis_client.delete(key))

# ComfyUI缓存管理器
class ComfyUICacheManager:
    """ComfyUI相关缓存管理器"""
    
    @staticmethod
    def cache_models(models: list, expire: int = 3600) -> bool:
        """
        缓存ComfyUI模型列表
        
        Args:
            models: 模型列表
            expire: 过期时间（秒，默认1小时）
        """
        key = "comfyui:models"
        return redis_client.set(key, models, expire)
    
    @staticmethod
    def get_cached_models() -> Optional[list]:
        """获取缓存的模型列表"""
        key = "comfyui:models"
        return redis_client.get(key)
    
    @staticmethod
    def delete_models_cache() -> bool:
        """删除模型缓存"""
        key = "comfyui:models"
        return bool(redis_client.delete(key))

# 导出管理器实例
task_progress_manager = TaskProgressManager()
user_cache_manager = UserCacheManager()
comfyui_cache_manager = ComfyUICacheManager()