# Pydantic 文件说明

本目录包含两个 Pydantic 相关的示例文件，各有侧重。

## 文件对比

| 文件 | 侧重点 | 适合人群 | 难度 |
|------|--------|----------|------|
| `pydantic_examples.py` | Pydantic 基础功能和常用场景 | 初学者 | ⭐⭐ |
| `pydantic-generic.py` | Pydantic 与泛型结合的高级用法 | 进阶学习者 | ⭐⭐⭐⭐ |

## pydantic_examples.py

**学习目标**: 掌握 Pydantic 的核心功能和实际应用

### 涵盖内容
1. ✅ **基础数据校验和类型转换**
   - 自动类型转换（字符串 → 数字、布尔值）
   - EmailStr、HttpUrl 等特殊类型
   
2. ✅ **自定义校验器**
   - `@field_validator` 字段级验证
   - `@model_validator` 模型级验证
   - 密码强度校验示例
   
3. ✅ **字段别名和序列化**
   - `alias` 接收时的字段别名
   - `serialization_alias` 序列化时的字段别名
   - 自定义序列化器
   
4. ✅ **嵌套模型**
   - 多层嵌套结构（订单-订单项-地址）
   - 枚举类型使用
   - 计算属性（@property）
   
5. ✅ **配置管理**
   - ConfigDict 配置
   - frozen（不可变配置）
   - 环境变量加载
   
6. ✅ **JSON Schema 生成**
   - 自动生成 API 文档
   - OpenAPI 集成

### 适用场景
- Web API 开发（FastAPI、Django）
- 配置文件管理
- 数据验证和清洗
- 表单验证
- API 响应格式化

### 运行示例
```bash
cd 03-python-basics
python pydantic_examples.py
```

## pydantic-generic.py

**学习目标**: 理解 Pydantic 与泛型结合，构建灵活的通用数据结构

### 涵盖内容
1. ✅ **泛型基础**
   - TypeVar 定义和使用
   - Generic[T] 泛型类
   
2. ✅ **通用分页器**
   - `Pagination[T]` 泛型分页模型
   - 支持任意类型的数据列表
   
3. ✅ **通用响应体**
   - `ApiResponse[T]` 统一响应格式
   - data 字段支持任意类型
   
4. ✅ **类型组合**
   - `ApiResponse[User]` 返回单个对象
   - `ApiResponse[Pagination[Goods]]` 返回分页列表
   - 嵌套泛型的灵活运用

### 核心价值
```python
# 同一个响应体，支持不同的数据类型
ApiResponse[User]              # 单个用户
ApiResponse[Pagination[Goods]] # 商品分页列表
ApiResponse[str]               # 字符串消息
ApiResponse[List[Tag]]         # 标签列表
```

### 适用场景
- RESTful API 设计
- 统一响应格式
- 分页数据处理
- 微服务接口规范
- 大型项目架构

### 运行示例
```bash
cd 03-python-basics
python pydantic-generic.py
```

## 学习路径建议

### 初学者路径
1. 先学习 `pydantic_examples.py`
   - 理解基础概念
   - 掌握常用功能
   - 熟悉实际应用场景

2. 再学习 `pydantic-generic.py`
   - 理解泛型的价值
   - 学习构建通用结构
   - 掌握高级设计模式

### 进阶路径
如果你已经熟悉 Pydantic：
1. 直接学习 `pydantic-generic.py`
2. 参考 `pydantic_examples.py` 查漏补缺

## 实际项目中的使用

### FastAPI 项目示例

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Generic, TypeVar, List

app = FastAPI()

# 使用泛型构建通用响应（来自 pydantic-generic.py）
T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int
    msg: str
    data: T | None = None

class User(BaseModel):
    id: int
    name: str
    email: str

# API 路由
@app.get("/users/{user_id}", response_model=ApiResponse[User])
async def get_user(user_id: int):
    user = User(id=user_id, name="张三", email="zhangsan@example.com")
    return ApiResponse(code=200, msg="成功", data=user)

@app.get("/users", response_model=ApiResponse[List[User]])
async def list_users():
    users = [
        User(id=1, name="张三", email="zhangsan@example.com"),
        User(id=2, name="李四", email="lisi@example.com")
    ]
    return ApiResponse(code=200, msg="成功", data=users)
```

## 相关文档

- `PYDANTIC_GUIDE.md` - Pydantic 完整使用指南
- [Pydantic 官方文档](https://docs.pydantic.dev/)

## 总结

| 特性 | pydantic_examples.py | pydantic-generic.py |
|------|---------------------|---------------------|
| 基础校验 | ✅ 详细讲解 | ✅ 简单使用 |
| 自定义验证器 | ✅ 多种示例 | ❌ 未涉及 |
| 泛型支持 | ❌ 未涉及 | ✅ 核心内容 |
| 嵌套模型 | ✅ 订单系统案例 | ✅ 泛型嵌套 |
| 配置管理 | ✅ ConfigDict | ❌ 未涉及 |
| 统一响应格式 | ❌ 未涉及 | ✅ 核心内容 |
| 难度 | ⭐⭐ 适合入门 | ⭐⭐⭐⭐ 需要泛型基础 |

**建议**: 两个文件结合学习，互为补充，掌握 Pydantic 的全面应用！
