from collections.abc import Mapping, MutableMapping, Iterable, Sequence

# 1. 查询 Mapping 必须实现的抽象方法
print("Mapping 必实现方法：", Mapping.__abstractmethods__)
# 输出：Mapping 必实现方法：frozenset({'__getitem__', '__iter__', '__len__'})

# 2. 查询 MutableMapping 必须实现的抽象方法
print("MutableMapping 必实现方法：", MutableMapping.__abstractmethods__)
# 输出：MutableMapping 必实现方法：frozenset({'__delitem__', '__setitem__', '__getitem__', '__iter__', '__len__'})

# 3. 查询 Iterable 必须实现的抽象方法
print("Iterable 必实现方法：", Iterable.__abstractmethods__)
# 输出：Iterable 必实现方法：frozenset({'__iter__'})

# 4. 查询 Sequence 必须实现的抽象方法
print("Sequence 必实现方法：", Sequence.__abstractmethods__)
# 输出：Sequence 必实现方法：frozenset({'__getitem__', '__len__'})