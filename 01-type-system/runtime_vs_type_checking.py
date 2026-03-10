"""
演示：运行时 vs 类型检查的区别
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

StateT = TypeVar("StateT", bound=Animal)

class PetStore(Generic[StateT]):
    def __init__(self, pet: StateT):
        self.pet = pet

    def get_pet(self) -> StateT:
        return self.pet

    def set_pet(self, new_pet: StateT) -> None:
        self.pet = new_pet

# ============================================================
# 演示：运行时允许类型混乱
# ============================================================

print("=" * 60)
print("演示：运行时允许类型混乱")
print("=" * 60)

print("\n1. 创建 dog_store（类型是 PetStore[Dog]）")
dog_store = PetStore(Dog("旺财"))
print(f"   dog_store = {dog_store}")
print(f"   dog_store.get_pet() = {dog_store.get_pet()}")
print(f"   dog_store.get_pet().bark() = {dog_store.get_pet().bark()}")

print("\n2. 类型混乱的赋值（运行时允许）")
animal_store: PetStore[Animal] = dog_store  # ← 类型不安全，但运行时允许
print(f"   ✅ 运行时允许：animal_store = {animal_store}")
print(f"   animal_store 和 dog_store 是同一个对象：{animal_store is dog_store}")

print("\n3. 通过 animal_store 放入 Cat（运行时允许）")
animal_store.set_pet(Cat("咪咪"))  # ← 类型不安全，但运行时允许
print(f"   ✅ 运行时允许：animal_store.get_pet() = {animal_store.get_pet()}")

print("\n4. 问题：dog_store 也被改变了！")
print(f"   dog_store.get_pet() = {dog_store.get_pet()}")
print(f"   dog_store 的类型是 PetStore[Dog]，但里面是 Cat！")
try:
    dog_store.get_pet().bark()  # ❌ 运行时错误：Cat 没有 bark 方法
except AttributeError as e:
    print(f"   ❌ 运行时错误：{e}")

# ============================================================
# 解释：为什么运行时允许？
# ============================================================

print("\n" + "=" * 60)
print("解释：为什么运行时允许？")
print("=" * 60)

print("""
Python 的类型注解在运行时被忽略：

1. 类型注解只是"注释"
   - Python 在运行时完全忽略类型注解
   - 类型注解不会影响程序的执行
   - 它们只是给开发者和工具看的

2. 运行时只关心值
   - Python 只检查对象是否有相应的方法/属性
   - 不检查类型是否匹配
   - 所以类型混乱的代码可以运行

3. 类型检查器的作用
   - mypy、pylance 等工具会在静态分析时检查类型
   - 它们会报告类型错误
   - 但不会阻止程序运行
""")

# ============================================================
# 演示：类型检查器会发现问题
# ============================================================

print("\n" + "=" * 60)
print("类型检查器会发现问题")
print("=" * 60)

print("""
如果使用类型检查器（如 mypy），会报告错误：

$ mypy test.py

test.py:38: error: Incompatible types in assignment (expression has type "PetStore[Dog]", variable has type "PetStore[Animal]")  [assignment]
    animal_store: PetStore[Animal] = dog_store
                                       ^
Found 1 error in 1 file (checked 1 source file)

类型检查器会：
1. 发现类型不匹配
2. 报告错误
3. 但不会阻止程序运行
""")

# ============================================================
# 演示：运行时类型检查（isinstance）
# ============================================================

print("\n" + "=" * 60)
print("运行时类型检查（isinstance）")
print("=" * 60)

print("\n1. 使用 isinstance 检查类型")
pet = dog_store.get_pet()
print(f"   pet = {pet}")
print(f"   isinstance(pet, Dog) = {isinstance(pet, Dog)}")
print(f"   isinstance(pet, Cat) = {isinstance(pet, Cat)}")
print(f"   isinstance(pet, Animal) = {isinstance(pet, Animal)}")

print("\n2. 在运行时检查类型（手动类型守卫）")
def safe_bark(store: PetStore[Animal]) -> str | None:
    """安全的 bark 方法"""
    pet = store.get_pet()
    if isinstance(pet, Dog):  # ← 运行时类型检查
        return pet.bark()
    else:
        return None

print(f"   safe_bark(dog_store) = {safe_bark(dog_store)}")
print(f"   safe_bark(animal_store) = {safe_bark(animal_store)}")

# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 60)
print("总结")
print("=" * 60)

print("""
✅ 关键理解：

1. Python 的类型注解在运行时被忽略
   - 类型混乱的代码可以运行
   - 但可能导致运行时错误

2. 类型检查器（静态分析）
   - mypy、pylance 等工具会检查类型
   - 在运行前发现类型错误
   - 但不会阻止程序运行

3. 运行时类型检查
   - 使用 isinstance() 检查类型
   - 在运行时动态检查
   - 可以避免类型错误

4. 最佳实践
   - 使用类型注解
   - 使用类型检查器（mypy）
   - 在关键位置使用 isinstance() 检查
   - 编写单元测试
""")




