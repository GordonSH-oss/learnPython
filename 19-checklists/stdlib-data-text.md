# 标准库：数据与文本

## `json`

- [ ] 我能在 Python 对象和 JSON 文本/字节之间转换。
- [ ] 我会使用 `dumps`、`loads`、`dump`、`load`、`ensure_ascii`、`default`。

```python
import json

payload = {"name": "Ada", "tags": ["python", "api"]}
text = json.dumps(payload, ensure_ascii=False)
decoded = json.loads(text)
print(decoded["tags"])
```

常见坑：JSON 不支持任意 Python 对象；`loads` 接受字符串，`load` 接受文件对象；不要把不可信 JSON 直接当成内部模型使用。

自查：JSON 中的元组会变成什么？如何处理 `datetime` 序列化？

练习：读取一个 JSON 配置，校验必填字段，并以 UTF-8 写回格式化 JSON。

仓库关联：[标准库组合示例](../03-python-basics/standard_library_tour.py)、[API 集成](../04-api-integration/README.md)。

## `csv`

- [ ] 我知道 CSV 是表格文本格式，字段可能包含逗号、换行和引号。
- [ ] 我会使用 `DictReader`、`DictWriter`、`newline=""` 和显式编码。

```python
import csv
from io import StringIO

source = StringIO("name,score\nAda,95\n")
rows = list(csv.DictReader(source))
print(rows[0]["name"], int(rows[0]["score"]))
```

常见坑：CSV 没有真正的类型系统；Windows 写文件时应使用 `newline=""`；列名和方言可能不同。

自查：为什么 `DictReader` 的值仍是字符串？如何处理缺失列？

练习：把字典列表写入 CSV，并在读取后把分数转换成整数。

仓库关联：扩展主题。

## `re` 与 `string`

- [ ] 我知道正则适合局部文本模式，不适合解析嵌套语言。
- [ ] 我会使用原始字符串、`compile`、`search`、`fullmatch`、命名组和 `Template`。

```python
import re
from string import Template

match = re.fullmatch(r"(?P<name>[A-Za-z]+)=(?P<value>\d+)", "score=95")
print(match.groupdict() if match else None)
print(Template("Hello, $name").substitute(name="Ada"))
```

常见坑：`match`、`search`、`fullmatch` 的范围不同；复杂正则要避免灾难性回溯；替换不可信文本时要考虑转义和注入。

自查：为什么正则模式通常写成原始字符串？什么时候用 `fullmatch` 而不是 `search`？

练习：解析 `key=value` 配置行，拒绝空键和非数字分数。

仓库关联：[模板处理](../03-python-basics/template-handle.py)、[标准库组合示例](../03-python-basics/standard_library_tour.py)。

## `sqlite3`

- [ ] 我能创建连接、执行参数化 SQL、提交事务并关闭连接。
- [ ] 我知道游标、事务和 SQL 注入的关系。

```python
import sqlite3

with sqlite3.connect(":memory:") as conn:
    conn.execute("create table users (id integer primary key, name text)")
    conn.execute("insert into users(name) values (?)", ("Ada",))
    print(conn.execute("select name from users").fetchall())
```

常见坑：不要用字符串拼接 SQL；连接上下文管理器会提交或回滚，但不会替你关闭所有长期连接；并发写入需要理解锁。

自查：`?` 参数为什么比 f-string 安全？什么时候应使用 ORM？

练习：实现带事务的新增和查询函数，并在唯一约束冲突时回滚。

仓库关联：[SQLite CRUD](../02-database/examples/sqlite/01_crud.py)、[事务](../02-database/examples/sqlite/02_transactions.py)。
