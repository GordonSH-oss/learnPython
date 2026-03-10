"""
TypeVar 的使用场景：不一定需要搭配 Generic
"""

from typing import TypeVar, Generic, List, Dict, Optional, Callable

class Animal:
    def __init__(self, name: str):
        self.name = name

class Dog(Animal):
    def bark(self) -> str:
        return f"{self.name}: Woof!"

# ============================================================
# 场景 1：搭配 Generic 使用（最常见）
# ============================================================

print("=" * 60)
print("场景 1：搭配 Generic 使用（最常见）")
print("=" * 60)

StateT = TypeVar("StateT", bound=Animal)

class PetStore(Generic[StateT]):
    """泛型类：使用 Generic"""
    def __init__(self, pet: StateT):
        self.pet = pet
    
    def get_pet(self) -> StateT:
        return self.pet

print("✅ 使用 Generic：")
print("   class PetStore(Generic[StateT]):")
print("   - 创建泛型类")
print("   - 可以在类定义中使用类型变量")
print()

# ============================================================
# 场景 2：单独在函数中使用（不需要 Generic）
# ============================================================

print("=" * 60)
print("场景 2：单独在函数中使用（不需要 Generic）")
print("=" * 60)

# 定义类型变量
T = TypeVar("T")

def identity(x: T) -> T:
    """泛型函数：返回输入的类型"""
    return x

def first_item(items: List[T]) -> Optional[T]:
    """泛型函数：返回列表第一个元素"""
    return items[0] if items else None

def swap(a: T, b: T) -> tuple[T, T]:
    """泛型函数：交换两个值"""
    return b, a

print("✅ 单独在函数中使用：")
print("   def identity(x: T) -> T:")
print("   - 不需要 Generic")
print("   - 直接在函数签名中使用")
print()

# 使用示例
result1 = identity(42)
result2 = identity("hello")
print(f"   identity(42) = {result1}, type = {type(result1)}")
print(f"   identity('hello') = {result2}, type = {type(result2)}")

# ============================================================
# 场景 3：在类型别名中使用
# ============================================================

print("\n" + "=" * 60)
print("场景 3：在类型别名中使用")
print("=" * 60)

from typing import TypeAlias

# 定义类型变量
KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")

# 类型别名（Python 3.10+）
# DictType: TypeAlias = Dict[KeyT, ValueT]  # 这样不行，需要函数形式

def create_dict_type(key_type: type[KeyT], value_type: type[ValueT]) -> type[Dict[KeyT, ValueT]]:
    """创建字典类型"""
    return Dict[key_type, value_type]

print("✅ 在类型别名中使用：")
print("   - 可以用于创建复杂的类型别名")
print("   - 但通常直接使用更简单")
print()

# ============================================================
# 场景 4：在方法中使用（类内部）
# ============================================================

print("=" * 60)
print("场景 4：在方法中使用（类内部）")
print("=" * 60)

class Container:
    """非泛型类，但方法可以使用 TypeVar"""
    
    def get_first(self, items: List[T]) -> Optional[T]:
        """方法中使用 TypeVar，不需要类本身是泛型"""
        return items[0] if items else None
    
    def merge(self, list1: List[T], list2: List[T]) -> List[T]:
        """合并两个列表"""
        return list1 + list2

print("✅ 在非泛型类的方法中使用：")
print("   class Container:")
print("       def get_first(self, items: List[T]) -> Optional[T]:")
print("   - 类本身不需要是 Generic")
print("   - 方法可以使用 TypeVar")
print()

container = Container()
result = container.get_first([1, 2, 3])
print(f"   container.get_first([1, 2, 3]) = {result}")

# ============================================================
# 场景 5：多个类型变量
# ============================================================

print("\n" + "=" * 60)
print("场景 5：多个类型变量")
print("=" * 60)

KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")

class KeyValueStore(Generic[KeyT, ValueT]):
    """使用多个类型变量的泛型类"""
    def __init__(self):
        self._store: Dict[KeyT, ValueT] = {}
    
    def set(self, key: KeyT, value: ValueT) -> None:
        self._store[key] = value
    
    def get(self, key: KeyT) -> Optional[ValueT]:
        return self._store.get(key)

print("✅ 多个类型变量：")
print("   class KeyValueStore(Generic[KeyT, ValueT]):")
print("   - 可以使用多个 TypeVar")
print("   - 每个类型变量独立")
print()

# ============================================================
# 场景 6：函数中使用，不需要 Generic
# ============================================================

print("=" * 60)
print("场景 6：函数中使用，不需要 Generic")
print("=" * 60)

def process_items(items: List[T], processor: Callable[[T], T]) -> List[T]:
    """处理列表中的每个元素"""
    return [processor(item) for item in items]

def find_item(items: List[T], predicate: Callable[[T], bool]) -> Optional[T]:
    """查找满足条件的元素"""
    for item in items:
        if predicate(item):
            return item
    return None

print("✅ 函数中使用 TypeVar：")
print("   def process_items(items: List[T], ...) -> List[T]:")
print("   - 不需要 Generic")
print("   - 直接在函数签名中使用")
print()

# 使用示例
numbers = [1, 2, 3, 4, 5]
doubled = process_items(numbers, lambda x: x * 2)
print(f"   process_items([1,2,3,4,5], lambda x: x*2) = {doubled}")

found = find_item(numbers, lambda x: x > 3)
print(f"   find_item([1,2,3,4,5], lambda x: x>3) = {found}")

# ============================================================
# 总结：什么时候需要 Generic？
# ============================================================

print("\n" + "=" * 60)
print("总结：什么时候需要 Generic？")
print("=" * 60)

print("""
✅ 需要 Generic 的情况：

1. 创建泛型类
   class PetStore(Generic[StateT]):
       def __init__(self, pet: StateT):
           self.pet = pet

2. 类的类型参数需要在多个地方使用
   - 类的属性类型
   - 方法的参数类型
   - 方法的返回类型

❌ 不需要 Generic 的情况：

1. 只在函数中使用 TypeVar
   def identity(x: T) -> T:
       return x

2. 只在方法中使用 TypeVar（类本身不是泛型）
   class Container:
       def get_first(self, items: List[T]) -> Optional[T]:
           return items[0]

3. 简单的类型约束
   def process(items: List[T]) -> List[T]:
       return items

✅ 关键理解：

- Generic：用于创建泛型类
- TypeVar：用于定义类型变量
- TypeVar 可以单独使用，不一定需要 Generic
- Generic 需要配合 TypeVar 使用
""")

# ============================================================
# 实际对比
# ============================================================

print("\n" + "=" * 60)
print("实际对比")
print("=" * 60)

print("\n1. 使用 Generic（泛型类）：")
print("   class PetStore(Generic[StateT]):")
print("       def __init__(self, pet: StateT): ...")
print("   - 类本身是泛型的")
print("   - 可以创建 PetStore[Dog]、PetStore[Cat] 等")

print("\n2. 不使用 Generic（普通类 + 泛型方法）：")
print("   class Container:")
print("       def get_first(self, items: List[T]) -> Optional[T]: ...")
print("   - 类本身不是泛型的")
print("   - 只有方法是泛型的")

print("\n3. 不使用 Generic（独立函数）：")
print("   def identity(x: T) -> T:")
print("       return x")
print("   - 函数是泛型的")
print("   - 不需要类")

