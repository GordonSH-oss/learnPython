from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

# 1. 定义泛型变量（支持任意类型）
T = TypeVar("T")

# 2. 第一步：定义通用分页器（泛型 + BaseModel）
#    作用：所有列表接口的分页数据都用这个结构，items 类型可灵活指定
class Pagination(BaseModel, Generic[T]):
    page: int = Field(ge=1, description="当前页码，最小为1")  # 校验：页码≥1
    size: int = Field(ge=1, le=100, description="每页条数，1-100")  # 校验：条数1-100
    total: int = Field(ge=0, description="总条数")  # 校验：总条数≥0
    items: List[T] = Field(description="当前页数据列表")  # 泛型T：列表项类型灵活指定

# 3. 第二步：定义通用响应体（泛型 + BaseModel）
#    作用：所有接口返回格式统一，data 类型可灵活指定（单个对象/分页数据/基础类型）
class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(description="状态码：200成功，400失败")
    msg: str = Field(description="提示信息")
    data: Optional[T] = Field(default=None, description="业务数据（任意类型）")  # 泛型T：业务数据类型灵活指定

# 4. 第三步：定义具体业务模型（纯 BaseModel，无泛型）
#    作用：固定结构的业务实体，做精准的数据校验
class User(BaseModel):
    id: int = Field(ge=1, description="用户ID")
    name: str = Field(min_length=1, max_length=20, description="用户名")
    age: Optional[int] = Field(ge=0, le=120, default=None, description="年龄")

class Goods(BaseModel):
    id: int = Field(ge=1, description="商品ID")
    name: str = Field(min_length=1, max_length=50, description="商品名")
    price: float = Field(ge=0.01, description="商品价格，最小0.01")

# 5. 第四步：业务场景使用（泛型 + BaseModel 结合的核心价值）
if __name__ == "__main__":
    # 场景1：返回单个用户数据（data=User）
    user = User(id=1, name="张三", age=25)
    user_resp: ApiResponse[User] = ApiResponse(
        code=200,
        msg="获取用户成功",
        data=user
    )
    print("=== 单个用户响应 ===")
    print(user_resp.model_dump_json(indent=2))  # 序列化：转格式化JSON

    # 场景2：返回商品分页数据（data=Pagination[Goods]）
    goods_list = [
        Goods(id=101, name="手机", price=1999.99),
        Goods(id=102, name="耳机", price=199.99)
    ]
    goods_pagination = Pagination(
        page=1,
        size=10,
        total=2,
        items=goods_list
    )
    goods_resp: ApiResponse[Pagination[Goods]] = ApiResponse(
        code=200,
        msg="获取商品列表成功",
        data=goods_pagination
    )
    print("\n=== 商品分页响应 ===")
    print(goods_resp.model_dump_json(indent=2))  # 序列化：转格式化JSON

    # 场景3：校验失败案例（体现 BaseModel 的校验能力）
    try:
        # 错误：页码<1，价格<0.01
        invalid_pagination = Pagination(
            page=0,  # 违反 ge=1 约束
            size=5,
            total=1,
            items=[Goods(id=103, name="数据线", price=0.001)]  # 价格违反 ge=0.01 约束
        )
    except Exception as e:
        print("\n=== 校验失败示例 ===")
        print(f"错误信息：{e}")