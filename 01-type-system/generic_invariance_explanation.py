"""
解释：泛型不变性（Invariance）和类型安全
"""

from typing import TypeVar, Generic

# ============================================================
# 类定义
# ============================================================

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

# 定义类型变量
StateT = TypeVar("StateT", bound=Animal)

class PetStore(Generic[StateT]):
    """可读写的宠物店（不变）"""
    def __init__(self, pet: StateT):
        self.pet = pet

    def get_pet(self) -> StateT:
        return self.pet

    def set_pet(self, new_pet: StateT) -> None:
        self.pet = new_pet

# ============================================================
# 解释第38行代码
# ============================================================

print("=" * 60)
print("解释：animal_store: PetStore[Animal] = dog_store")
print("=" * 60)

print("""
这行代码的含义：

1. dog_store 的类型：
   dog_store = PetStore(Dog("旺财"))
   # dog_store 的类型是 PetStore[Dog]

2. animal_store 的类型注解：
   animal_store: PetStore[Animal]
   # 声明 animal_store 应该是 PetStore[Animal] 类型

3. 赋值操作：
   animal_store: PetStore[Animal] = dog_store
   # 试图将 PetStore[Dog] 赋值给 PetStore[Animal] 类型的变量

4. 问题：
   - Dog 是 Animal 的子类（Dog <: Animal）
   - 但 PetStore[Dog] 不能赋值给 PetStore[Animal]
   - 这是因为 PetStore 是"不变"的（invariant）
""")

# ============================================================
# 为什么会有问题？
# ============================================================

print("\n" + "=" * 60)
print("为什么会有问题？")
print("=" * 60)

print("""
如果允许这个赋值，会发生什么：

1. dog_store 原本只应该存储 Dog
   dog_store = PetStore(Dog("旺财"))
   # dog_store 的类型是 PetStore[Dog]

2. 赋值给 animal_store
   animal_store: PetStore[Animal] = dog_store
   # 现在 animal_store 和 dog_store 指向同一个对象

3. 通过 animal_store 放入 Cat
   animal_store.set_pet(Cat("咪咪"))
   # 因为 animal_store 的类型是 PetStore[Animal]
   # 所以可以放入 Animal 的子类 Cat

4. 问题：dog_store 也被改变了！
   # dog_store 和 animal_store 指向同一个对象
   # 所以 dog_store 里现在也是 Cat
   # 但 dog_store 的类型是 PetStore[Dog]，不应该有 Cat！

这就是类型不安全的原因。
""")

# ============================================================
# 实际演示
# ============================================================

print("\n" + "=" * 60)
print("实际演示")
print("=" * 60)

print("\n1. 创建 dog_store")
dog_store = PetStore(Dog("旺财"))
print(f"   dog_store = {dog_store}")
print(f"   dog_store.get_pet() = {dog_store.get_pet()}")
print(f"   dog_store.get_pet().bark() = {dog_store.get_pet().bark()}")

print("\n2. 赋值给 animal_store（类型不安全的操作）")
animal_store: PetStore[Animal] = dog_store  # ← 这行代码
print(f"   animal_store = {animal_store}")
print(f"   animal_store 和 dog_store 是同一个对象：{animal_store is dog_store}")

print("\n3. 通过 animal_store 放入 Cat")
animal_store.set_pet(Cat("咪咪"))
print(f"   animal_store.get_pet() = {animal_store.get_pet()}")

print("\n4. 检查 dog_store（也被改变了！）")
print(f"   dog_store.get_pet() = {dog_store.get_pet()}")
print(f"   dog_store 的类型是 PetStore[Dog]，但里面是 Cat！")
try:
    dog_store.get_pet().bark()  # ❌ Cat 没有 bark 方法
except AttributeError as e:
    print(f"   ❌ 错误：{e}")

# ============================================================
# 类型不变性（Invariance）
# ============================================================

print("\n" + "=" * 60)
print("类型不变性（Invariance）")
print("=" * 60)

print("""
Python 的 Generic 默认是"不变"的（invariant）：

1. 不变性（Invariance）：
   - PetStore[Dog] 不能赋值给 PetStore[Animal]
   - 即使 Dog 是 Animal 的子类
   - 这是为了保证类型安全

2. 协变性（Covariance）：
   - 如果允许 PetStore[Dog] <: PetStore[Animal]
   - 就会导致上面的类型安全问题

3. 逆变性（Contravariance）：
   - 相反的方向
   - 在某些场景下有用，但这里不适用

为什么 PetStore 是不变的？
- PetStore 既有 get（读取）又有 set（写入）
- 如果允许协变，写入操作会破坏类型安全
- 所以必须是不变的
""")

# ============================================================
# 运行时 vs 类型检查
# ============================================================

print("\n" + "=" * 60)
print("运行时 vs 类型检查")
print("=" * 60)

print("""
1. 运行时（Runtime）：
   - Python 在运行时忽略类型注解
   - 所以 animal_store: PetStore[Animal] = dog_store 能执行
   - 但这是类型不安全的

2. 类型检查器（Type Checker）：
   - mypy、pylance 等工具会检查类型
   - 会报错：Incompatible types in assignment
   - 提示这是类型不安全的操作

3. 注释说明：
   # 运行时能执行，但类型逻辑错误
   - 运行时不会阻止
   - 但类型检查器会报错
   - 这是类型不安全的
""")

# ============================================================
# 正确的做法
# ============================================================

print("\n" + "=" * 60)
print("正确的做法")
print("=" * 60)

print("""
1. 保持类型一致：
   dog_store: PetStore[Dog] = PetStore(Dog("旺财"))
   # 不要赋值给 PetStore[Animal]

2. 如果需要 Animal 类型：
   animal_store: PetStore[Animal] = PetStore(Animal("动物"))
   # 或者
   animal_store: PetStore[Animal] = PetStore(Dog("旺财"))
   # 但这样会丢失 Dog 的特定方法

3. 使用类型转换（如果确定安全）：
   from typing import cast
   animal_store = cast(PetStore[Animal], dog_store)
   # 但这是不安全的，不推荐
""")

# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 60)
print("总结")
print("=" * 60)

print("""
✅ 第38行代码的含义：

animal_store: PetStore[Animal] = dog_store

1. 试图将 PetStore[Dog] 赋值给 PetStore[Animal]
2. 运行时能执行（Python 忽略类型注解）
3. 但类型检查器会报错（类型不安全）
4. 会导致类型安全问题（可以往 Dog store 里放 Cat）

✅ 关键理解：

- PetStore 是不变的（invariant）
- PetStore[Dog] ≠ PetStore[Animal]
- 即使 Dog 是 Animal 的子类
- 这是为了保证类型安全
""")

