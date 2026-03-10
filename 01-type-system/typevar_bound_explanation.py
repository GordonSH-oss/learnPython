"""
解释：TypeVar 的 bound 参数
"""

from typing import TypeVar, Generic

class Animal:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Animal({self.name})"

class Dog(Animal):
    def bark(self) -> str:
        return f"{self.name}: Woof!"

class Cat(Animal):
    def meow(self) -> str:
        return f"{self.name}: Meow!"

class Plant:  # 不是 Animal 的子类
    def __init__(self, name: str):
        self.name = name

# ============================================================
# 对比：有 bound vs 没有 bound
# ============================================================

print("=" * 60)
print("对比：有 bound vs 没有 bound")
print("=" * 60)

# 没有 bound 的 TypeVar
UnboundedT = TypeVar("UnboundedT")

# 有 bound 的 TypeVar
StateT = TypeVar("StateT", bound=Animal)

print("\n1. 没有 bound 的 TypeVar")
print("   UnboundedT = TypeVar('UnboundedT')")
print("   - 可以是任何类型")
print("   - 没有限制")

print("\n2. 有 bound 的 TypeVar")
print("   StateT = TypeVar('StateT', bound=Animal)")
print("   - 必须是 Animal 或其子类")
print("   - 限制类型范围")

# ============================================================
# bound 的作用：限制类型范围
# ============================================================

print("\n" + "=" * 60)
print("bound 的作用：限制类型范围")
print("=" * 60)

class PetStore(Generic[StateT]):
    """PetStore 使用 StateT，StateT 必须是 Animal 或其子类"""
    def __init__(self, pet: StateT):
        self.pet = pet

    def get_pet(self) -> StateT:
        return self.pet

    def set_pet(self, new_pet: StateT) -> None:
        self.pet = new_pet

print("\n✅ 允许的类型（Animal 及其子类）：")
print("   PetStore[Animal]  ✅")
print("   PetStore[Dog]     ✅ (Dog 是 Animal 的子类)")
print("   PetStore[Cat]     ✅ (Cat 是 Animal 的子类)")

print("\n❌ 不允许的类型（不是 Animal 的子类）：")
print("   PetStore[int]     ❌ (int 不是 Animal)")
print("   PetStore[str]     ❌ (str 不是 Animal)")
print("   PetStore[Plant]   ❌ (Plant 不是 Animal 的子类)")

# ============================================================
# 实际演示
# ============================================================

print("\n" + "=" * 60)
print("实际演示")
print("=" * 60)

print("\n1. 创建 PetStore[Animal]")
animal_store = PetStore(Animal("动物"))
print(f"   ✅ 成功：animal_store = {animal_store}")

print("\n2. 创建 PetStore[Dog]")
dog_store = PetStore(Dog("旺财"))
print(f"   ✅ 成功：dog_store = {dog_store}")
print(f"   ✅ Dog 是 Animal 的子类，所以允许")

print("\n3. 创建 PetStore[Cat]")
cat_store = PetStore(Cat("咪咪"))
print(f"   ✅ 成功：cat_store = {cat_store}")
print(f"   ✅ Cat 是 Animal 的子类，所以允许")

# ============================================================
# bound 的含义
# ============================================================

print("\n" + "=" * 60)
print("bound 的含义")
print("=" * 60)

print("""
StateT = TypeVar("StateT", bound=Animal)

含义：
1. StateT 是一个类型变量
2. bound=Animal 表示：
   - StateT 必须是 Animal 或其子类
   - 不能是 Animal 的父类
   - 不能是其他不相关的类型

类比：
- bound = "上界"（upper bound）
- StateT 可以是 Animal 或 Animal 的子类
- 但不能超过 Animal 这个"上界"

例子：
- PetStore[Dog]    ✅ (Dog <: Animal)
- PetStore[Cat]    ✅ (Cat <: Animal)
- PetStore[Animal] ✅ (Animal = Animal)
- PetStore[int]    ❌ (int 不是 Animal)
- PetStore[Plant]  ❌ (Plant 不是 Animal 的子类)
""")

# ============================================================
# 为什么需要 bound？
# ============================================================

print("\n" + "=" * 60)
print("为什么需要 bound？")
print("=" * 60)

print("""
1. 类型安全：
   - 确保类型变量只能是特定类型或其子类
   - 避免使用不相关的类型

2. 代码提示：
   - IDE 知道 StateT 至少是 Animal
   - 可以提供 Animal 的方法提示

3. 方法调用：
   - 可以安全地调用 Animal 的方法
   - 因为 StateT 保证是 Animal 或其子类

例子：
class PetStore(Generic[StateT]):
    def get_pet(self) -> StateT:
        return self.pet
    
    def get_name(self) -> str:
        # ✅ 可以调用 self.pet.name
        # 因为 StateT 有 bound=Animal，保证有 name 属性
        return self.pet.name
""")

# ============================================================
# 对比：bound vs 没有 bound
# ============================================================

print("\n" + "=" * 60)
print("对比：bound vs 没有 bound")
print("=" * 60)

class UnboundedStore(Generic[UnboundedT]):
    def __init__(self, item: UnboundedT):
        self.item = item

class BoundedStore(Generic[StateT]):
    def __init__(self, pet: StateT):
        self.pet = pet
    
    def get_name(self) -> str:
        # ✅ 可以安全调用，因为 StateT 有 bound=Animal
        return self.pet.name

print("\n1. 没有 bound：")
print("   UnboundedStore[int]     ✅")
print("   UnboundedStore[str]     ✅")
print("   UnboundedStore[Animal]  ✅")
print("   任何类型都可以")

print("\n2. 有 bound=Animal：")
print("   BoundedStore[Animal]    ✅")
print("   BoundedStore[Dog]       ✅")
print("   BoundedStore[Cat]       ✅")
print("   BoundedStore[int]       ❌ (mypy 会报错)")
print("   只能是 Animal 或其子类")

# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 60)
print("总结")
print("=" * 60)

print("""
✅ 关键理解：

1. bound=Animal 的作用：
   - 限制类型变量的范围
   - StateT 必须是 Animal 或其子类
   - 不能是其他类型

2. 为什么叫 bound（上界）：
   - Animal 是类型的"上界"
   - StateT 不能超过这个上界
   - 但可以是 Animal 的子类

3. 实际效果：
   - PetStore[Dog]    ✅ (Dog 是 Animal 的子类)
   - PetStore[Cat]    ✅ (Cat 是 Animal 的子类)
   - PetStore[int]    ❌ (int 不是 Animal)

4. 好处：
   - 类型安全
   - IDE 代码提示
   - 可以安全调用 Animal 的方法

记住：
- bound=Animal 表示"必须是 Animal 或其子类"
- 这是类型变量的"上界"限制
""")


