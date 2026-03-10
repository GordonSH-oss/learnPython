#!/usr/bin/env python3
"""演示如何正确导入和使用 learn_typing 模块"""

print("=== 方法1：使用模块名前缀 ===")
import learn_typing
print(f"learn_typing.my_list: {learn_typing.my_list}")
print(f"learn_typing.my_dict: {learn_typing.my_dict}")

print("\n=== 方法2：使用 from import ===")
from learn_typing import my_list, my_dict, my_optional
print(f"my_list: {my_list}")
print(f"my_dict: {my_dict}")

print("\n=== 方法3：导入所有（不推荐）===")
# 注意：这需要模块定义 __all__，否则会导入所有不以下划线开头的名称
from learn_typing import *
print(f"my_list: {my_list}")
print(f"my_dict: {my_dict}")

print("\n=== 查看模块中所有可用的名称 ===")
print([name for name in dir(learn_typing) if not name.startswith('_')])

