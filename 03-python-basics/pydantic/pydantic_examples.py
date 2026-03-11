"""
Pydantic 实用案例集合

展示 Pydantic 的常用功能：
1. 数据校验和类型转换
2. 自定义校验器
3. 字段别名和序列化
4. 嵌套模型
5. 配置管理
6. JSON Schema 生成
"""

from pydantic import (
    BaseModel, 
    Field, 
    field_validator,
    model_validator,
    ConfigDict,
    EmailStr,
    HttpUrl,
    field_serializer
)
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================
# 案例 1: 基础数据校验和类型转换
# ============================================================
print("=" * 60)
print("案例 1: 基础数据校验和类型转换")
print("=" * 60)

class UserRegistration(BaseModel):
    """用户注册模型 - 展示基础校验和类型转换"""
    username: str = Field(min_length=3, max_length=20, description="用户名")
    email: EmailStr = Field(description="邮箱地址")
    age: int = Field(ge=18, le=120, description="年龄，必须18-120岁")
    website: Optional[HttpUrl] = Field(default=None, description="个人网站")
    is_active: bool = Field(default=True, description="是否激活")

# 正常情况
user1 = UserRegistration(
    username="zhangsan",
    email="zhangsan@example.com",
    age="25",  # 字符串会自动转换为 int
    website="https://example.com",
    is_active="yes"  # 字符串会转换为 bool
)
print(f"用户1: {user1}")
print(f"类型转换: age={user1.age} (type: {type(user1.age).__name__})")
print(f"类型转换: is_active={user1.is_active} (type: {type(user1.is_active).__name__})")

# 校验失败情况
try:
    user2 = UserRegistration(
        username="ab",  # 太短，违反 min_length=3
        email="invalid-email",  # 无效邮箱
        age=15  # 未满18岁
    )
except Exception as e:
    print(f"\n❌ 校验失败: {e}")


# ============================================================
# 案例 2: 自定义校验器
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 自定义校验器 - 密码强度校验")
print("=" * 60)

class UserWithPassword(BaseModel):
    """带密码的用户模型 - 展示自定义校验"""
    username: str
    password: str = Field(min_length=8, description="密码")
    confirm_password: str = Field(description="确认密码")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """字段级校验器：检查密码强度"""
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """模型级校验器：检查两次密码是否一致"""
        if self.password != self.confirm_password:
            raise ValueError('两次输入的密码不一致')
        return self

# 成功案例
user_pwd = UserWithPassword(
    username="user123",
    password="StrongPass123",
    confirm_password="StrongPass123"
)
print(f"✅ 密码校验通过: {user_pwd.username}")

# 失败案例：密码强度不够
try:
    weak_user = UserWithPassword(
        username="user456",
        password="weakpass",  # 没有大写字母和数字
        confirm_password="weakpass"
    )
except Exception as e:
    print(f"❌ 密码强度校验失败: {e}")

# 失败案例：密码不一致
try:
    mismatch_user = UserWithPassword(
        username="user789",
        password="StrongPass123",
        confirm_password="DifferentPass123"
    )
except Exception as e:
    print(f"❌ 密码不一致: {e}")


# ============================================================
# 案例 3: 字段别名和序列化配置
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 字段别名和序列化配置")
print("=" * 60)

class Article(BaseModel):
    """文章模型 - 展示字段别名和序列化"""
    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用字段名或别名
        str_strip_whitespace=True  # 自动去除字符串首尾空格
    )
    
    id: int = Field(alias="article_id")  # 接收时使用别名
    title: str = Field(min_length=1, max_length=100)
    content: str
    author_id: int = Field(serialization_alias="author")  # 序列化时使用别名
    created_at: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """自定义序列化：将 datetime 转换为指定格式"""
        return dt.strftime("%Y-%m-%d %H:%M:%S")

# 使用别名接收数据
article_data = {
    "article_id": 1,  # 使用别名
    "title": "  Pydantic 教程  ",  # 有空格，会自动去除
    "content": "这是内容",
    "author_id": 100,
    "created_at": "2024-01-01 10:00:00"
}
article = Article(**article_data)
print(f"文章标题（已去空格）: '{article.title}'")

# 序列化时使用别名
print("\n序列化结果:")
print(article.model_dump_json(indent=2, by_alias=True))


# ============================================================
# 案例 4: 嵌套模型和关系
# ============================================================
print("\n" + "=" * 60)
print("案例 4: 嵌套模型 - 订单系统")
print("=" * 60)

class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Address(BaseModel):
    """地址模型"""
    province: str
    city: str
    district: str
    detail: str
    
    def full_address(self) -> str:
        """返回完整地址"""
        return f"{self.province}{self.city}{self.district}{self.detail}"

class OrderItem(BaseModel):
    """订单项模型"""
    product_id: int
    product_name: str
    quantity: int = Field(ge=1, description="数量")
    unit_price: float = Field(ge=0, description="单价")
    
    @property
    def subtotal(self) -> float:
        """计算小计"""
        return self.quantity * self.unit_price

class Order(BaseModel):
    """订单模型 - 嵌套多个子模型"""
    order_id: str
    customer_name: str
    shipping_address: Address  # 嵌套地址模型
    items: List[OrderItem] = Field(min_length=1, description="订单项列表")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    
    @property
    def total_amount(self) -> float:
        """计算订单总金额"""
        return sum(item.subtotal for item in self.items)

# 创建订单
order = Order(
    order_id="ORD20240301001",
    customer_name="李四",
    shipping_address={
        "province": "北京市",
        "city": "北京市",
        "district": "朝阳区",
        "detail": "某某街道123号"
    },
    items=[
        {"product_id": 1, "product_name": "iPhone 15", "quantity": 1, "unit_price": 5999.00},
        {"product_id": 2, "product_name": "AirPods Pro", "quantity": 2, "unit_price": 1999.00}
    ]
)

print(f"订单号: {order.order_id}")
print(f"客户: {order.customer_name}")
print(f"收货地址: {order.shipping_address.full_address()}")
print(f"订单状态: {order.status.value}")
print("\n订单明细:")
for item in order.items:
    print(f"  - {item.product_name} x{item.quantity} = ¥{item.subtotal:.2f}")
print(f"订单总金额: ¥{order.total_amount:.2f}")


# ============================================================
# 案例 5: 配置管理
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 配置管理 - 应用配置")
print("=" * 60)

class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str = Field(default="localhost")
    port: int = Field(default=5432, ge=1, le=65535)
    username: str
    password: str
    database: str
    
    def get_connection_string(self) -> str:
        """生成数据库连接字符串"""
        return f"postgresql://{self.username}:{'*' * len(self.password)}@{self.host}:{self.port}/{self.database}"

class RedisConfig(BaseModel):
    """Redis 配置"""
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0, ge=0, le=15)

class AppConfig(BaseModel):
    """应用配置 - 嵌套多个配置模块"""
    model_config = ConfigDict(
        frozen=True,  # 配置不可变
        validate_assignment=True  # 赋值时也进行校验
    )
    
    app_name: str
    debug: bool = Field(default=False)
    database: DatabaseConfig
    redis: RedisConfig
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")

# 从字典或 JSON 创建配置
config_data = {
    "app_name": "MyApp",
    "debug": True,
    "database": {
        "host": "db.example.com",
        "port": 5432,
        "username": "admin",
        "password": "secret123",
        "database": "myapp_db"
    },
    "redis": {
        "host": "redis.example.com",
        "port": 6379,
        "db": 1
    },
    "log_level": "DEBUG"
}

config = AppConfig(**config_data)
print(f"应用: {config.app_name}")
print(f"调试模式: {config.debug}")
print(f"数据库: {config.database.get_connection_string()}")
print(f"Redis: {config.redis.host}:{config.redis.port}/{config.redis.db}")
print(f"日志级别: {config.log_level}")

# 尝试修改配置（frozen=True 会阻止修改）
try:
    config.debug = False
except Exception as e:
    print(f"\n❌ 配置不可变: {type(e).__name__}")


# ============================================================
# 案例 6: JSON Schema 生成
# ============================================================
print("\n" + "=" * 60)
print("案例 6: 生成 JSON Schema")
print("=" * 60)

import json

# 生成 JSON Schema（用于 API 文档）
schema = Order.model_json_schema()
print("Order 模型的 JSON Schema:")
print(json.dumps(schema, indent=2, ensure_ascii=False))


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("Pydantic 核心特性总结")
print("=" * 60)
print("""
1. 自动类型转换和校验
2. 自定义校验器（字段级、模型级）
3. 字段别名和序列化配置
4. 嵌套模型支持
5. 配置管理（不可变配置）
6. JSON Schema 自动生成
7. 性能优化（基于 Rust）

常用场景：
- API 请求/响应验证
- 配置文件管理
- 数据库 ORM
- 表单验证
- 数据序列化/反序列化
""")