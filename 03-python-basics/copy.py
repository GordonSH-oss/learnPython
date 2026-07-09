import importlib.util
import sysconfig
from pathlib import Path


def load_stdlib_copy():
    """加载标准库 copy 模块，避免被当前文件 copy.py 遮蔽。"""
    copy_path = Path(sysconfig.get_path("stdlib")) / "copy.py"
    spec = importlib.util.spec_from_file_location("stdlib_copy", copy_path)
    copy_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(copy_module)
    return copy_module


# 注意：本文件也叫 copy.py，直接 import copy 会导入当前文件自己。
# 实际项目中建议把文件改名为 copy_demo.py，然后直接写：import copy
copy_module = load_stdlib_copy()

# Python 中的“拷贝”通常有 3 种情况：
# 1. 赋值：不会创建新对象，只是让两个变量指向同一个对象。
# 2. 浅拷贝：创建一个新的外层对象，但里面的嵌套可变对象仍然共用。
# 3. 深拷贝：递归创建新对象，外层对象和嵌套可变对象都不共用。

print("===== 赋值：两个变量指向同一个对象 =====")
a = [1, 2, [3, 4]]
b = a

b[0] = 99
b[2][0] = 999

print("a:", a)  # [99, 2, [999, 4]]
print("b:", b)  # [99, 2, [999, 4]]
print("a is b:", a is b)  # True

print("\n===== 浅拷贝：只拷贝外层对象 =====")
a = [1, 2, [3, 4]]
b = copy_module.copy(a)

b[0] = 99
b[2][0] = 999

print("a:", a)  # [1, 2, [999, 4]]
print("b:", b)  # [99, 2, [999, 4]]
print("a is b:", a is b)  # False，外层列表不是同一个对象
print("a[2] is b[2]:", a[2] is b[2])  # True，内层列表仍然是同一个对象

print("\n===== 深拷贝：外层和内层对象都拷贝 =====")
a = [1, 2, [3, 4]]
b = copy_module.deepcopy(a)

b[0] = 99
b[2][0] = 999

print("a:", a)  # [1, 2, [3, 4]]
print("b:", b)  # [99, 2, [999, 4]]
print("a is b:", a is b)  # False，外层列表不是同一个对象
print("a[2] is b[2]:", a[2] is b[2])  # False，内层列表也不是同一个对象

# 记忆方式：
# - 只有一层普通列表/字典时，浅拷贝通常够用。
# - 有嵌套列表、嵌套字典等可变对象时，如果不想互相影响，用深拷贝。
