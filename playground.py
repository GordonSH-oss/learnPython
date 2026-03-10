from pydantic import BaseModel, Field
import math

class Circle(BaseModel):
    radius: float = Field(ge=0)

    # 计算周长（纯计算，无存储）
    @property
    def perimeter(self):
        return 2 * math.pi * self.radius

    # 计算面积（纯计算，无存储）
    @property
    def area(self):
        return math.pi * (self.radius **2)

c = Circle(radius=2)
print(c.perimeter)  # 12.566...（像普通属性一样访问）
print(c.area)       # 12.566...