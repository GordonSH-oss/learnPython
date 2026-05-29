"""
上下文管理器示例 - 对应 context-managers.md
运行：python context_manager.py
"""

from contextlib import contextmanager, suppress
import os
import tempfile


# ── 1. with 语句基础 ──────────────────────────────────────────────────────────

print("=== 1. with 语句：文件安全读写 ===")
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    tmp_path = f.name
    f.write("hello\nworld\n")

with open(tmp_path) as f:
    for line in f:
        print(f"  读到：{line.rstrip()}")

os.unlink(tmp_path)


# ── 2. 类实现上下文管理器 ─────────────────────────────────────────────────────

class Timer:
    """计时上下文管理器"""
    import time

    def __enter__(self):
        import time
        self._start = time.perf_counter()
        return self  # with Timer() as t: 中 t 就是 self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.perf_counter() - self._start
        if exc_type is not None:
            print(f"  [Timer] 发生异常：{exc_type.__name__}，耗时 {self.elapsed:.4f}s")
        else:
            print(f"  [Timer] 耗时 {self.elapsed:.4f}s")
        return False  # 不抑制异常

print("\n=== 2. 类实现上下文管理器 ===")
with Timer() as t:
    total = sum(range(1_000_000))
print(f"  计算结果：{total}")

print("\n  异常情况：")
try:
    with Timer():
        raise ValueError("模拟错误")
except ValueError:
    print("  异常已传播出来")


# ── 3. @contextmanager 生成器实现 ─────────────────────────────────────────────

@contextmanager
def temp_directory():
    """创建临时目录，退出时自动清理"""
    import tempfile, shutil
    tmpdir = tempfile.mkdtemp()
    print(f"  创建临时目录：{tmpdir}")
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)
        print(f"  已清理：{tmpdir}")

print("\n=== 3. @contextmanager ===")
with temp_directory() as d:
    test_file = os.path.join(d, "test.txt")
    with open(test_file, "w") as f:
        f.write("临时数据")
    print(f"  写入文件：{test_file}")
print(f"  目录是否还存在：{os.path.exists(d)}")


# ── 4. contextlib.suppress ────────────────────────────────────────────────────

print("\n=== 4. suppress：静默忽略指定异常 ===")
with suppress(FileNotFoundError):
    os.remove("/tmp/nonexistent_file_xyz.txt")
    print("  这行不会执行")
print("  suppress 后继续执行，无异常抛出")


# ── 5. 异常处理 + 上下文管理器组合 ───────────────────────────────────────────

@contextmanager
def transaction(name):
    """模拟事务：成功提交，失败回滚"""
    print(f"  [事务] 开始：{name}")
    try:
        yield
        print(f"  [事务] 提交：{name}")
    except Exception as e:
        print(f"  [事务] 回滚：{name}，原因：{e}")
        raise

print("\n=== 5. 事务上下文管理器 ===")
print("  成功场景：")
with transaction("插入用户"):
    print("  执行 INSERT ...")

print("\n  失败场景：")
try:
    with transaction("更新余额"):
        print("  执行 UPDATE ...")
        raise RuntimeError("余额不足")
except RuntimeError:
    print("  外层捕获到异常")
