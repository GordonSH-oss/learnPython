"""
*args 和 **kwargs 详解

理解 Python 函数参数的顺序规则和使用方法
"""

# ============================================================
# 案例 1: 参数顺序规则
# ============================================================
print("=" * 60)
print("案例 1: 参数顺序规则 - 为什么顺序很重要？")
print("=" * 60)

def func(*args, **kwargs):
    """接收任意数量的位置参数和关键字参数"""
    print(f"  位置参数 args: {args}")
    print(f"  关键字参数 kwargs: {kwargs}")

print("✅ 正确的顺序：位置参数在前，关键字参数在后")
func(1, 2, 3, 4, 5, a=1, b=2, c=3)

print("\n❌ 错误的顺序：关键字参数在前会导致语法错误")
print("func(a=1, b=2, c=3, 1, 2, 3, 4, 5)  # SyntaxError!")

try:
    # 这行代码会导致语法错误，无法运行
    # func(a=1, b=2, c=3, 1, 2, 3, 4, 5)
    exec("func(a=1, b=2, c=3, 1, 2, 3, 4, 5)")
except SyntaxError as e:
    print(f"  错误: {e}")


# ============================================================
# 案例 2: Python 函数参数的完整顺序
# ============================================================
print("\n" + "=" * 60)
print("案例 2: 完整的参数顺序规则")
print("=" * 60)

def complete_function(
    pos1,                    # 1. 位置参数
    pos2,                    # 2. 位置参数
    *args,                   # 3. 可变位置参数
    kw1,                     # 4. 关键字参数（keyword-only）
    kw2="default",           # 5. 带默认值的关键字参数
    **kwargs                 # 6. 可变关键字参数
):
    print(f"  位置参数: pos1={pos1}, pos2={pos2}")
    print(f"  可变位置参数 args: {args}")
    print(f"  关键字参数: kw1={kw1}, kw2={kw2}")
    print(f"  可变关键字参数 kwargs: {kwargs}")

print("正确调用:")
complete_function(1, 2, 3, 4, 5, kw1="a", kw2="b", extra1="x", extra2="y")


# ============================================================
# 案例 3: 为什么必须这样排序？
# ============================================================
print("\n" + "=" * 60)
print("案例 3: 排序规则的原因")
print("=" * 60)

print("""
Python 解析参数的顺序：
1. 先匹配位置参数（从左到右）
2. 再匹配关键字参数（通过名称）

如果允许 func(a=1, 2, 3)，Python 无法判断：
- 2 和 3 应该赋值给哪个参数？
- 位置参数的顺序是什么？

因此，Python 强制要求：
✅ func(1, 2, 3, a=1, b=2)  # 先位置，后关键字
❌ func(a=1, b=2, 1, 2, 3)  # 语法错误
""")


# ============================================================
# 案例 4: 不同类型参数的示例
# ============================================================
print("=" * 60)
print("案例 4: 各种参数类型的使用")
print("=" * 60)

def demo(a, b, *args, c, d=10, **kwargs):
    """
    a, b: 必需的位置参数
    *args: 额外的位置参数
    c: 必需的关键字参数（keyword-only）
    d: 可选的关键字参数（有默认值）
    **kwargs: 额外的关键字参数
    """
    print(f"  a={a}, b={b}")
    print(f"  args={args}")
    print(f"  c={c}, d={d}")
    print(f"  kwargs={kwargs}")

print("调用 1: 最少参数")
demo(1, 2, c=3)

print("\n调用 2: 更多位置参数")
demo(1, 2, 3, 4, 5, c=3)

print("\n调用 3: 带默认值和额外关键字参数")
demo(1, 2, 3, 4, c=3, d=20, e=100, f=200)


# ============================================================
# 案例 5: 常见错误
# ============================================================
print("\n" + "=" * 60)
print("案例 5: 常见错误示例")
print("=" * 60)

def example(*args, **kwargs):
    print(f"args: {args}, kwargs: {kwargs}")

print("错误 1: 关键字参数在位置参数之前")
print("example(a=1, 2, 3)  # ❌ SyntaxError")

print("\n错误 2: 位置参数在关键字参数之后")
print("example(1, 2, a=3, 4)  # ❌ SyntaxError")

print("\n正确的用法:")
example(1, 2, 3, a=4, b=5, c=6)


# ============================================================
# 案例 6: 解包时的顺序
# ============================================================
print("\n" + "=" * 60)
print("案例 6: 解包时的顺序规则")
print("=" * 60)

def func2(a, b, c, d, e):
    print(f"  a={a}, b={b}, c={c}, d={d}, e={e}")

# 解包列表和字典
args_list = [1, 2, 3]
kwargs_dict = {'d': 4, 'e': 5}

print("✅ 正确: 先解包位置参数，后解包关键字参数")
func2(*args_list, **kwargs_dict)

print("\n❌ 错误: 顺序反了会怎样？")
try:
    # func2(**kwargs_dict, *args_list)  # 语法错误
    exec("func2(**kwargs_dict, *args_list)")
except SyntaxError as e:
    print(f"  错误: 语法错误，*args 必须在 **kwargs 之前")


# ============================================================
# 案例 7: 实际应用场景
# ============================================================
print("\n" + "=" * 60)
print("案例 7: 实际应用场景")
print("=" * 60)

# 场景 1: 包装函数
def log_function_call(func):
    """装饰器：记录函数调用"""
    def wrapper(*args, **kwargs):
        print(f"  → 调用函数 {func.__name__}")
        print(f"    位置参数: {args}")
        print(f"    关键字参数: {kwargs}")
        result = func(*args, **kwargs)
        print(f"  ← 返回: {result}")
        return result
    return wrapper

@log_function_call
def add(a, b, c=0):
    return a + b + c

print("使用装饰器:")
result = add(1, 2, c=3)

# 场景 2: 可变参数的求和
def smart_sum(*numbers, initial=0):
    """
    求和函数
    *numbers: 位置参数（要相加的数字）
    initial: 关键字参数（初始值）
    """
    total = initial
    for num in numbers:
        total += num
    return total

print("\n\n可变参数求和:")
print(f"  smart_sum(1, 2, 3, 4, 5) = {smart_sum(1, 2, 3, 4, 5)}")
print(f"  smart_sum(1, 2, 3, initial=10) = {smart_sum(1, 2, 3, initial=10)}")

# 场景 3: 构建 API 调用
def api_request(endpoint, *params, method="GET", timeout=30, **headers):
    """
    模拟 API 请求
    endpoint: 必需位置参数
    *params: 额外的路径参数
    method: 关键字参数（请求方法）
    timeout: 关键字参数（超时时间）
    **headers: 额外的请求头
    """
    url = f"https://api.example.com/{endpoint}"
    if params:
        url += "/" + "/".join(str(p) for p in params)
    
    print(f"\n  发送 {method} 请求到: {url}")
    print(f"  超时: {timeout}s")
    if headers:
        print(f"  请求头: {headers}")

print("\n\nAPI 请求示例:")
api_request("users", 123, "posts", method="POST", timeout=60, 
            Authorization="Bearer token", Content_Type="application/json")


# ============================================================
# 案例 8: Python 3.8+ 的新特性
# ============================================================
print("\n" + "=" * 60)
print("案例 8: 仅限位置参数（Python 3.8+）")
print("=" * 60)

def func_with_positional_only(a, b, /, c, d, *, e, f):
    """
    a, b: 仅限位置参数（/之前）
    c, d: 可以是位置或关键字参数
    e, f: 仅限关键字参数（*之后）
    """
    print(f"  a={a}, b={b}, c={c}, d={d}, e={e}, f={f}")

print("正确调用:")
func_with_positional_only(1, 2, 3, 4, e=5, f=6)
func_with_positional_only(1, 2, c=3, d=4, e=5, f=6)

print("\n错误示例:")
try:
    # a, b 不能用关键字传递
    func_with_positional_only(a=1, b=2, c=3, d=4, e=5, f=6)
except TypeError as e:
    print(f"  ❌ {e}")


# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("参数顺序规则总结")
print("=" * 60)
print("""
📌 完整的参数顺序（从左到右）:

1. 仅限位置参数 (positional-only, Python 3.8+)
   def func(a, b, /, ...):

2. 位置或关键字参数 (positional or keyword)
   def func(a, b, ...):

3. *args (可变位置参数)
   def func(*args, ...):

4. 仅限关键字参数 (keyword-only)
   def func(*, a, b, ...):

5. **kwargs (可变关键字参数)
   def func(**kwargs):

完整示例:
def func(pos_only1, pos_only2, /,
         pos_or_kw1, pos_or_kw2,
         *args,
         kw_only1, kw_only2,
         **kwargs):
    pass

✅ 调用时的规则:
- 位置参数必须在关键字参数之前
- *args 必须在 **kwargs 之前
- 一旦使用了关键字参数，后面都必须是关键字参数

❌ 常见错误:
func(a=1, 2, 3)       # 语法错误
func(1, 2, a=3, 4)    # 语法错误
func(**kw, *args)     # 语法错误

💡 记忆技巧:
"先位置，后关键字" - Position before Keyword
"先值，后名" - Value before Name
""")


# ============================================================
# 案例 9: 实用的设计模式
# ============================================================
print("=" * 60)
print("案例 9: 实用的设计模式")
print("=" * 60)

# 模式 1: 灵活的构造函数
class User:
    """用户类，支持多种初始化方式"""
    def __init__(self, name, *tags, age=None, email=None, **metadata):
        self.name = name
        self.tags = tags
        self.age = age
        self.email = email
        self.metadata = metadata
    
    def __repr__(self):
        return f"User(name='{self.name}', tags={self.tags}, age={self.age}, email='{self.email}', metadata={self.metadata})"

print("创建用户对象:")
user1 = User("Alice", "admin", "developer", age=30, email="alice@example.com", 
             city="Beijing", department="Engineering")
print(f"  {user1}")

# 模式 2: 配置合并
def create_config(**defaults):
    """创建配置，允许覆盖默认值"""
    def get_config(**overrides):
        config = {**defaults, **overrides}
        return config
    return get_config

print("\n配置合并:")
get_db_config = create_config(host="localhost", port=5432, user="admin")
config1 = get_db_config()
print(f"  默认配置: {config1}")
config2 = get_db_config(host="192.168.1.100", password="secret")
print(f"  覆盖配置: {config2}")


# ============================================================
# 案例 10: 调试技巧
# ============================================================
print("\n" + "=" * 60)
print("案例 10: 调试和检查参数")
print("=" * 60)

import inspect

def debug_args(*args, **kwargs):
    """调试函数：显示所有参数信息"""
    frame = inspect.currentframe()
    args_info = inspect.getargvalues(frame)
    
    print("  参数详情:")
    print(f"    args 类型: {type(args)}")
    print(f"    args 内容: {args}")
    print(f"    args 长度: {len(args)}")
    
    print(f"\n    kwargs 类型: {type(kwargs)}")
    print(f"    kwargs 内容: {kwargs}")
    print(f"    kwargs 长度: {len(kwargs)}")

print("调试参数:")
debug_args(1, 2, 3, a="x", b="y", c="z")

print("""

🔍 调试技巧:
1. 打印 args 和 kwargs 查看实际接收的参数
2. 使用 locals() 查看所有局部变量
3. 使用 inspect 模块获取详细信息
4. 添加类型提示帮助 IDE 检查
""")
