"""
Python 模块加载机制可运行教材

运行方式：
    python 03-python-basics/module_loading_tutorial.py

学习目标：
    1. 理解 import 不是简单复制代码，而是“查找 -> 加载 -> 执行 -> 缓存”。
    2. 理解 sys.path 的搜索顺序，以及为什么当前目录里的 copy.py 会遮蔽标准库 copy。
    3. 学会用 __file__、sys.modules、importlib.util.find_spec() 诊断模块从哪里来。
    4. 学会在必要时从指定文件路径加载一个模块。
"""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
import sysconfig
import tempfile
import textwrap
from pathlib import Path


LINE = "=" * 72


def title(text: str) -> None:
    print(f"\n{LINE}\n{text}\n{LINE}")


def write_file(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def run_python(script: Path, cwd: Path | None = None) -> str:
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.stdout.rstrip()


def remove_module(module_name: str) -> None:
    """从模块缓存中移除模块，方便重复演示 import 的真实加载过程。"""
    sys.modules.pop(module_name, None)


def lesson_1_import_executes_once(workspace: Path) -> None:
    title("1. import 会执行模块文件，但同一个进程里默认只执行一次")

    write_file(
        workspace / "demo_counter.py",
        """
        print("demo_counter.py 正在执行")
        value = 1
        """,
    )

    sys.path.insert(0, str(workspace))
    remove_module("demo_counter")
    try:
        print("第一次 import demo_counter：")
        import demo_counter

        print("第二次 import demo_counter：")
        import demo_counter as same_module

        print("demo_counter is same_module:", demo_counter is same_module)
        print("demo_counter.value:", demo_counter.value)
        print("sys.modules 里是否有 demo_counter:", "demo_counter" in sys.modules)
    finally:
        remove_module("demo_counter")
        sys.path.remove(str(workspace))

    print(
        """
结论：
  - import 第一次找到模块文件后，会执行模块顶层代码。
  - 执行完成后，模块对象会放进 sys.modules 缓存。
  - 同一进程中再次 import 同名模块时，通常直接复用 sys.modules 里的对象。
"""
    )


def lesson_2_sys_path_search_order(workspace: Path) -> None:
    title("2. sys.path 决定模块搜索顺序：前面的目录优先")

    dir_a = workspace / "dir_a"
    dir_b = workspace / "dir_b"
    dir_a.mkdir()
    dir_b.mkdir()

    write_file(dir_a / "toolbox.py", 'source = "来自 dir_a/toolbox.py"\n')
    write_file(dir_b / "toolbox.py", 'source = "来自 dir_b/toolbox.py"\n')

    remove_module("toolbox")
    sys.path[:0] = [str(dir_a), str(dir_b)]
    try:
        import toolbox

        print("sys.path 中 dir_a 在 dir_b 前面")
        print("toolbox.source:", toolbox.source)
        print("toolbox.__file__:", toolbox.__file__)
    finally:
        remove_module("toolbox")
        sys.path.remove(str(dir_a))
        sys.path.remove(str(dir_b))

    sys.path[:0] = [str(dir_b), str(dir_a)]
    try:
        import toolbox

        print("\nsys.path 中 dir_b 在 dir_a 前面")
        print("toolbox.source:", toolbox.source)
        print("toolbox.__file__:", toolbox.__file__)
    finally:
        remove_module("toolbox")
        sys.path.remove(str(dir_b))
        sys.path.remove(str(dir_a))

    print(
        """
结论：
  - Python 会按 sys.path 从前到后查找模块。
  - 找到第一个匹配的模块后就停止。
  - 如果两个目录里都有同名模块，前面的目录胜出。
"""
    )


def lesson_3_shadowing_stdlib(workspace: Path) -> None:
    title("3. 命名遮蔽：项目里的 copy.py 会遮蔽标准库 copy")

    project = workspace / "shadow_project"
    project.mkdir()

    write_file(
        project / "copy.py",
        """
        print("项目自己的 copy.py 被加载了")
        name = "local copy.py"
        """,
    )
    write_file(
        project / "main.py",
        """
        import copy
        import importlib.util
        import sys

        print("sys.path[0]:", sys.path[0])
        print("copy.__file__:", copy.__file__)
        print("copy.name:", getattr(copy, "name", "<没有 name>"))
        print("copy.copy 是否存在:", hasattr(copy, "copy"))
        print("find_spec('copy').origin:", importlib.util.find_spec("copy").origin)
        """,
    )

    print(run_python(project / "main.py", cwd=project))

    print(
        """
结论：
  - 运行脚本时，脚本所在目录通常会放在 sys.path 的最前面。
  - 当前目录里如果有 copy.py，import copy 会优先导入这个文件。
  - 这就是为什么学习深拷贝/浅拷贝时，把文件命名为 copy.py 容易出问题。
  - 更推荐把示例文件命名为 copy_demo.py、copy_examples.py 等。
"""
    )


def lesson_4_diagnose_module_source() -> None:
    title("4. 诊断模块来源：__file__、__spec__、find_spec()")

    import json

    spec = importlib.util.find_spec("json")

    print("json.__file__:", json.__file__)
    print("json.__spec__.origin:", json.__spec__.origin)
    print("find_spec('json').origin:", spec.origin if spec else None)
    print("json 是否在 sys.modules:", "json" in sys.modules)

    print(
        """
调试技巧：
  - print(module.__file__)：看当前导入的模块文件路径。
  - importlib.util.find_spec("模块名")：看 Python 准备从哪里加载模块。
  - "模块名" in sys.modules：看模块是否已经被当前进程缓存。
"""
    )


def lesson_5_reload(workspace: Path) -> None:
    title("5. importlib.reload() 可以重新执行已加载模块")

    module_path = workspace / "settings.py"
    write_file(
        module_path,
        """
        print("settings.py 正在执行")
        version = 1
        """,
    )

    sys.path.insert(0, str(workspace))
    remove_module("settings")
    try:
        import settings

        print("第一次导入 version:", settings.version)

        write_file(
            module_path,
            """
            print("settings.py 重新执行")
            version = 2
            changed = "第二版模块多了一个变量，用来让文件大小发生变化"
            """,
        )

        importlib.invalidate_caches()
        reloaded = importlib.reload(settings)
        print("reload 后 version:", reloaded.version)
        print("reload 后 changed:", reloaded.changed)
        print("settings is reloaded:", settings is reloaded)
    finally:
        remove_module("settings")
        sys.path.remove(str(workspace))

    print(
        """
结论：
  - importlib.reload(module) 会在原模块对象上重新执行模块代码。
  - reload 常用于调试或交互式实验，不建议作为业务代码的常规设计手段。
  - Python 可能使用 __pycache__ 里的字节码缓存；快速改写同名文件时，
    文件时间戳和大小都要能体现变化，reload 才能稳定看到新代码。
"""
    )


def lesson_6_load_from_exact_path() -> None:
    title("6. 从指定路径加载模块：绕过普通 import 的搜索顺序")

    stdlib_copy_path = Path(sysconfig.get_path("stdlib")) / "copy.py"
    spec = importlib.util.spec_from_file_location("stdlib_copy_for_demo", stdlib_copy_path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载标准库 copy 模块: {stdlib_copy_path}")

    stdlib_copy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stdlib_copy)

    original = [1, 2, [3, 4]]
    copied = stdlib_copy.deepcopy(original)
    copied[2][0] = 999

    print("标准库 copy.py 路径:", stdlib_copy_path)
    print("original:", original)
    print("copied:", copied)
    print("original[2] is copied[2]:", original[2] is copied[2])

    print(
        """
结论：
  - importlib.util.spec_from_file_location() 可以从一个明确文件路径加载模块。
  - 这适合教学、插件系统、动态加载等场景。
  - 日常代码更推荐避免同名文件冲突，而不是依赖这种绕路加载方式。
"""
    )


def main() -> None:
    print(__doc__)
    with tempfile.TemporaryDirectory(prefix="module_loading_") as tmp:
        workspace = Path(tmp)
        lesson_1_import_executes_once(workspace)
        lesson_2_sys_path_search_order(workspace)
        lesson_3_shadowing_stdlib(workspace)
        lesson_4_diagnose_module_source()
        lesson_5_reload(workspace)
        lesson_6_load_from_exact_path()

    title("总结")
    print(
        """
模块加载的核心模型：
  1. 查找：按 sys.path、内置模块、包路径等规则找到模块规格。
  2. 加载：创建模块对象。
  3. 执行：执行模块顶层代码，生成函数、类、变量等名称。
  4. 缓存：把模块对象放进 sys.modules，后续 import 直接复用。

排查导入问题时先问 3 个问题：
  1. 我实际导入的是哪个文件？看 module.__file__。
  2. Python 为什么会找到它？看 sys.path 顺序。
  3. 它是不是已经被缓存了？看 sys.modules。
"""
    )


if __name__ == "__main__":
    main()
