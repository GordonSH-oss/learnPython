# 环境、依赖和项目结构

学习 Python 项目时，先把“代码如何被运行、依赖如何被安装、配置如何进入程序”这三件事理清楚。否则后面的 Web、数据库、AI 示例会变成零散脚本，难以复用。

## 学习目标

- 会创建和激活虚拟环境。
- 知道 `requirements/` 中不同依赖清单的用途。
- 能把配置从环境变量读入程序，而不是写死在代码里。
- 能区分脚本、模块、包和项目入口。
- 能解释为什么测试和示例不应该依赖真实密钥。

## 本目录文件

- `config_example.py`：用标准库读取环境变量，构造类型明确的配置对象。

## 推荐命令

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements/base.txt
python 00-environment/config_example.py
```

如果只学习标准库示例，可以先不安装依赖。

## 心智模型

```text
shell environment
  -> os.environ
  -> Settings object
  -> application code
```

代码应该依赖 `Settings`，而不是在业务逻辑里到处调用 `os.environ[...]`。这样测试时可以直接构造配置对象，不需要污染全局环境。

## 练习

1. 增加一个 `LOG_LEVEL` 配置项，默认值为 `INFO`。
2. 把 `APP_PORT` 设置成非数字，观察程序如何报错。
3. 写一个 `from_mapping()` 方法，用普通字典创建 `Settings`，方便单元测试。
