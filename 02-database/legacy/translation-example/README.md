# 原有翻译项目数据库示例

这里保存整理前的 SQLAlchemy 与持久化示例，领域模型是翻译任务、文档 chunk 和上下文数据。

这些文件适合在完成主课程后用于代码阅读。它们包含 SQLAlchemy 1.x 风格，例如 `sqlalchemy.ext.declarative.declarative_base()` 和传统 `session.query()`。新项目优先参考 `../../examples/sqlalchemy/` 中的 SQLAlchemy 2.x 写法。

部分模型使用 PostgreSQL UUID 类型，即使教程脚本把 URL 改成 SQLite，也可能存在方言兼容问题。不要把这些文件当作通用模板直接复制到生产项目。

