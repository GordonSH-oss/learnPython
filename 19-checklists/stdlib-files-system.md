# 标准库：文件与系统

## `pathlib`

- [ ] 我知道它用路径对象统一文件系统路径操作。
- [ ] 我会使用 `Path`、`/` 拼接、`glob()`、`read_text()`、`write_text()`、`mkdir()`。

```python
from pathlib import Path

root = Path("data")
root.mkdir(exist_ok=True)
target = root / "example.txt"
target.write_text("hello\n", encoding="utf-8")
print(target.read_text(encoding="utf-8"))
```

常见坑：路径存在不代表它是预期类型；文本读写要明确编码；处理不可信路径时要防止目录穿越。

自查：为什么新代码通常优先 `pathlib`？`resolve()` 与 `absolute()` 的语义有什么不同？

练习：递归查找目录内所有 `.md` 文件，并统计总行数。

仓库关联：[标准库组合示例](../03-python-basics/standard_library_tour.py)。

## `os` 与 `sys`

- [ ] 我知道 `os` 面向操作系统接口，`sys` 面向解释器和进程运行环境。
- [ ] 我会使用 `os.environ`、`os.walk()`、`sys.argv`、`sys.path`、`sys.version_info`。

```python
import os
import sys

debug = os.environ.get("APP_DEBUG", "false").lower() == "true"
print(debug, sys.version_info[:2], sys.argv[1:])
```

常见坑：环境变量都是字符串；直接修改 `sys.path` 往往说明项目结构或安装方式有问题；`os.path` 接受字符串，而 `pathlib` 提供对象接口。

自查：什么时候仍应使用 `os.path`？为什么密钥不能写入代码或日志？

练习：从环境变量读取端口，缺失时使用默认值，并对非法整数给出清晰错误。

仓库关联：[环境配置](../00-environment/config_example.py)、[模块加载](../03-python-basics/module_loading_tutorial.py)。

## `shutil` 与 `tempfile`

- [ ] 我知道 `shutil` 提供高层文件操作，`tempfile` 安全创建临时资源。
- [ ] 我会使用 `copy2()`、`copytree()`、`move()`、`make_archive()`、`TemporaryDirectory()`。

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

with TemporaryDirectory() as temp_dir:
    source = Path(temp_dir) / "source.txt"
    source.write_text("backup", encoding="utf-8")
    shutil.copy2(source, Path(temp_dir) / "copy.txt")
```

常见坑：复制和删除前必须确认目标；临时目录离开上下文后会被清理；不要自己拼接可预测的临时文件名。

自查：`copy()` 与 `copy2()` 有何差异？为什么测试中适合使用临时目录？

练习：将一个目录复制到临时目录，打包为 ZIP，并在退出上下文前验证归档存在。

仓库关联：扩展主题。

## `subprocess`

- [ ] 我知道它用于创建和管理外部进程。
- [ ] 我会使用 `run()`、`Popen`、`check=True`、`capture_output=True`、`text=True`、`timeout`。

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "--version"],
    check=True,
    capture_output=True,
    text=True,
    timeout=5,
)
print(result.stdout or result.stderr)
```

常见坑：优先传参数列表并避免 `shell=True`；必须处理非零退出码和超时；长时间运行或大量输出的进程需要正确消费管道。

自查：`check=True` 改变了什么？用户输入与 `shell=True` 组合为何危险？

练习：调用当前 Python 解释器执行一段最小代码，并分别处理成功、非零退出和超时。

仓库关联：[C 示例运行脚本](../18-c-extensions/c-language/scripts/run_examples.sh) 可作为外部命令场景参考。

