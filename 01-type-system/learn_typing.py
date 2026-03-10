# Python 3.9+ 现代写法（推荐）
from typing import Any  # Any 仍然需要从 typing 导入

# ✅ 使用内置类型（Python 3.9+）
my_list: list[int] = [1, 2, 3, 4, 5]
my_dict: dict[str, int] = {"a": 1, "b": 2, "c": 3}
my_optional: int | None = 1  # Python 3.10+ 使用 | 语法
# 或者: my_optional: Optional[int] = 1  # 旧写法，仍然可用但不推荐
my_any: Any = "hello"

# ❌ 旧写法（Python 3.9 之前，已过时但还能用）
# from typing import List, Dict, Optional
# my_list: List[int] = [1, 2, 3, 4, 5]
# my_dict: Dict[str, int] = {"a": 1, "b": 2, "c": 3}
# my_optional: Optional[int] = 1

print(my_list)
print(my_dict)
print(my_optional)
print(my_any)