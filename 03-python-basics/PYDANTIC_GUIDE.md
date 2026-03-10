# Pydantic 使用指南

## 什么是 Pydantic？

Pydantic 是一个用于数据验证和设置管理的 Python 库，使用 Python 类型注解来验证数据。

### 核心优势
- ⚡ **快速**: 基于 Rust 重写的核心，性能优异
- 🔒 **类型安全**: 利用 Python 类型注解进行验证
- 🎯 **易用**: API 简洁直观
- 🔄 **自动转换**: 自动进行类型转换
- 📝 **IDE 支持**: 完美支持类型提示和自动补全

## 安装

```bash
# 基础安装
pip install pydantic

# 带邮箱验证支持
pip install pydantic[email]

# Pydantic V2（推荐）
pip install "pydantic>=2.0"
```

## 快速开始

### 基础模型

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# 创建实例
user = User(id=1, name="张三", email="zhangsan@example.com")

# 自动类型转换
user2 = User(id="2", name="李四", email="lisi@example.com")
print(user2.id)  # 2 (int 类型)
```

### 数据验证

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, description="价格必须大于0")
    stock: int = Field(ge=0, description="库存不能为负数")

# ✅ 验证通过
product = Product(name="手机", price=1999.99, stock=100)

# ❌ 验证失败
try:
    invalid_product = Product(name="", price=-10, stock=-5)
except Exception as e:
    print(f"验证失败: {e}")
```

## 常用功能

### 1. 字段验证器

#### Field 约束
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    # 字符串约束
    username: str = Field(min_length=3, max_length=20)
    
    # 数字约束
    age: int = Field(ge=0, le=120)  # ge: >=, le: <=
    score: float = Field(gt=0, lt=100)  # gt: >, lt: <
    
    # 正则表达式
    phone: str = Field(pattern=r'^\d{11}$')
```

#### 自定义验证器
```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str
    password: str
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        assert v.isalnum(), '用户名必须是字母数字组合'
        return v
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含大写字母')
        return v
```

### 2. 特殊类型

```python
from pydantic import BaseModel, EmailStr, HttpUrl, UUID4
from datetime import datetime
from typing import Optional

class UserProfile(BaseModel):
    email: EmailStr  # 邮箱验证
    website: Optional[HttpUrl] = None  # URL 验证
    user_id: UUID4  # UUID 验证
    created_at: datetime  # 日期时间
```

### 3. 嵌套模型

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str

class Company(BaseModel):
    name: str
    address: Address

class Employee(BaseModel):
    name: str
    company: Company
    skills: List[str]

# 创建嵌套对象
employee = Employee(
    name="张三",
    company={
        "name": "某公司",
        "address": {
            "street": "中关村大街1号",
            "city": "北京",
            "country": "中国"
        }
    },
    skills=["Python", "Django", "FastAPI"]
)
```

### 4. 序列化和反序列化

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# 创建对象
user = User(id=1, name="张三", email="zhangsan@example.com")

# 转换为字典
user_dict = user.model_dump()
print(user_dict)
# {'id': 1, 'name': '张三', 'email': 'zhangsan@example.com'}

# 转换为 JSON
user_json = user.model_dump_json(indent=2)
print(user_json)

# 从 JSON 解析
json_str = '{"id": 2, "name": "李四", "email": "lisi@example.com"}'
user2 = User.model_validate_json(json_str)
```

### 5. 字段别名

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    # 接收 item_id，存储为 id
    id: int = Field(alias='item_id')
    
    # 序列化时使用 itemName
    name: str = Field(serialization_alias='itemName')

# 使用别名接收数据
item = Item(item_id=1, name="商品")

# 序列化时使用别名
print(item.model_dump(by_alias=True))
# {'item_id': 1, 'itemName': '商品'}
```

### 6. 配置选项

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 去除字符串空格
        validate_assignment=True,   # 赋值时验证
        frozen=True,                # 不可变
        populate_by_name=True,      # 允许使用字段名或别名
    )
    
    name: str
    email: str

user = User(name="  张三  ", email="zhangsan@example.com")
print(user.name)  # "张三" (已去除空格)

# frozen=True 阻止修改
try:
    user.name = "李四"
except Exception as e:
    print(f"错误: {type(e).__name__}")
```

### 7. 模型级验证器

```python
from pydantic import BaseModel, model_validator

class PasswordReset(BaseModel):
    password: str
    confirm_password: str
    
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('两次密码不一致')
        return self

# ✅ 验证通过
valid = PasswordReset(password="Pass123", confirm_password="Pass123")

# ❌ 验证失败
try:
    invalid = PasswordReset(password="Pass123", confirm_password="Pass456")
except Exception as e:
    print(f"错误: {e}")
```

## 实际应用场景

### 1. FastAPI 路由参数验证

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    age: int = Field(ge=18)

@app.post("/users")
async def create_user(user: CreateUserRequest):
    # Pydantic 自动验证请求体
    return {"message": "用户创建成功", "user": user}
```

### 2. 配置管理

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"  # 从 .env 文件读取

# 自动从环境变量或 .env 文件加载
settings = Settings()
```

### 3. API 响应模型

```python
from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    name: str
    email: str

class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[User] = None

class PaginatedResponse(BaseModel):
    code: int
    message: str
    data: List[User]
    total: int
    page: int
    page_size: int
```

## Pydantic V1 vs V2

### 主要变化

| 功能 | V1 | V2 |
|------|----|----|
| 性能 | Python 实现 | Rust 核心 |
| 字典转换 | `.dict()` | `.model_dump()` |
| JSON 转换 | `.json()` | `.model_dump_json()` |
| 从字典创建 | `.parse_obj()` | `.model_validate()` |
| 从 JSON 创建 | `.parse_raw()` | `.model_validate_json()` |
| 验证器装饰器 | `@validator` | `@field_validator` |

### 迁移建议

如果你使用 Pydantic V1，建议升级到 V2：

```bash
# 安装 V2
pip install "pydantic>=2.0"

# 使用迁移工具
pip install bump-pydantic
bump-pydantic /path/to/your/code
```

## 最佳实践

### 1. 使用类型注解
```python
from typing import Optional, List
from pydantic import BaseModel

class User(BaseModel):
    name: str  # 必填
    email: Optional[str] = None  # 可选
    tags: List[str] = []  # 默认空列表
```

### 2. 添加描述信息
```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(description="商品名称")
    price: float = Field(gt=0, description="商品价格，必须大于0")
    stock: int = Field(ge=0, description="库存数量")
```

### 3. 复用验证逻辑
```python
from pydantic import BaseModel, field_validator

def validate_phone(v: str) -> str:
    if not v.isdigit() or len(v) != 11:
        raise ValueError('手机号必须是11位数字')
    return v

class User(BaseModel):
    phone: str
    
    _validate_phone = field_validator('phone')(validate_phone)

class Employee(BaseModel):
    phone: str
    
    _validate_phone = field_validator('phone')(validate_phone)
```

### 4. 合理使用配置
```python
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # 自动去空格
        validate_assignment=True,   # 赋值时验证
        extra='forbid'              # 禁止额外字段
    )
```

## 学习资源

- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [Pydantic GitHub](https://github.com/pydantic/pydantic)
- [FastAPI 文档](https://fastapi.tiangolo.com/) - 大量使用 Pydantic
- [Pydantic V2 迁移指南](https://docs.pydantic.dev/latest/migration/)

## 相关文件

- `pydantic_examples.py` - 6个实用案例，涵盖主要功能
- `pydantic-generic.py` - Pydantic 与泛型结合使用

## 运行示例

```bash
cd 03-python-basics

# 运行基础案例
python pydantic_examples.py

# 运行泛型案例
python pydantic-generic.py
```
